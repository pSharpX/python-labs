"""Word document generation with python-docx.

The service validates that approval is present and current *before* writing anything,
renders only approved structured data (plus LLM prose that carries no figures), and
stores each version under ``<output_dir>/<proposal_id>/v<document_version>/``.
Earlier versions are never overwritten.
"""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from src.shared import ApprovalStatus
from src.services.version_service import approval_is_valid, estimate_fingerprint

from settings import DocumentSettings
from src.shared import NarrativeDraft
from src.shared.models import ApprovalRecord, DocumentMetadata, RequirementsSpecification, TechnicalProposal, \
    FinancialEstimate
from src.utils.hashing import file_sha256, utcnow


class DocumentGenerationError(RuntimeError):
    pass


@dataclass
class DocumentInput:
    proposal_id: str
    document_version: int
    title: str
    customer_name: str
    requirements: RequirementsSpecification
    technical: TechnicalProposal
    estimate: FinancialEstimate
    approval: ApprovalRecord | None
    narrative: NarrativeDraft


_SAFE = re.compile(r"[^A-Za-z0-9_.-]")


def _money(value: Decimal, currency: str) -> str:
    return f"{currency} {value:,.2f}"


def _pct(rate: Decimal) -> str:
    return f"{(rate * 100).normalize():f}%"


def _hours(value: Decimal) -> str:
    return f"{value.normalize():f}" if value == value.to_integral() else f"{value:.1f}"


class DocumentService:
    def __init__(self, settings: DocumentSettings, output_dir: Path) -> None:
        self._s = settings
        self._out = Path(output_dir).resolve()

    @property
    def output_dir(self) -> Path:
        return self._out

    def resolve(self, relative_path: str) -> Path:
        """Resolve a stored relative path, refusing anything outside the output dir."""
        candidate = (self._out / relative_path).resolve()
        if self._out not in candidate.parents:
            raise DocumentGenerationError("Document path escapes the output directory")
        return candidate

    # ---- public API ------------------------------------------------------------------
    def generate(self, data: DocumentInput) -> DocumentMetadata:
        if not approval_is_valid(data.requirements, data.technical, data.estimate, data.approval):
            raise DocumentGenerationError(
                "An approved final document requires a current approval of this exact estimate version"
            )
        assert data.approval is not None

        safe_id = _SAFE.sub("_", data.proposal_id)
        folder = self._out / safe_id / f"v{data.document_version}"
        folder.mkdir(parents=True, exist_ok=True)
        filename = f"proposal_{safe_id}_v{data.document_version}.docx"
        target = folder / filename
        if target.exists():
            raise DocumentGenerationError(f"Document version {data.document_version} already exists")

        doc = self._build(data)
        fd, tmp = tempfile.mkstemp(suffix=".docx", dir=folder)
        os.close(fd)
        try:
            doc.save(tmp)
            os.replace(tmp, target)
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

        return DocumentMetadata(
            proposal_id=data.proposal_id,
            document_version=data.document_version,
            filename=filename,
            file_path=str(target.relative_to(self._out)),
            created_at=utcnow(),
            approval_status=ApprovalStatus.APPROVED,
            content_hash=file_sha256(target),
            requirements_version=data.requirements.version,
            technical_version=data.technical.version,
            estimate_version=data.estimate.version,
            estimate_fingerprint=estimate_fingerprint(data.estimate),
        )

    # ---- building blocks -------------------------------------------------------------
    def _color(self, hex_value: str) -> RGBColor:
        return RGBColor.from_string(hex_value.strip("#").upper())

    def _setup_styles(self, doc: Document) -> None:
        styles = doc.styles
        normal = styles["Normal"]
        normal.font.name = self._s.font_name
        normal.font.size = Pt(10.5)
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), self._s.font_name)
        normal.paragraph_format.space_after = Pt(6)
        normal.paragraph_format.line_spacing = 1.15
        for level, size in ((1, 18), (2, 14), (3, 12)):
            st = styles[f"Heading {level}"]
            st.font.name = self._s.font_name
            st.font.size = Pt(size)
            st.font.bold = True
            st.font.color.rgb = self._color(self._s.primary_color if level < 3 else self._s.accent_color)
            st.paragraph_format.space_before = Pt(14 if level == 1 else 10)
            st.paragraph_format.space_after = Pt(6)
            st.paragraph_format.keep_with_next = True

    @staticmethod
    def _field(paragraph, code: str) -> None:  # type: ignore[no-untyped-def]
        run = paragraph.add_run()
        begin = OxmlElement("w:fldChar")
        begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = code
        sep = OxmlElement("w:fldChar")
        sep.set(qn("w:fldCharType"), "separate")
        txt = OxmlElement("w:t")
        txt.text = "1"
        end = OxmlElement("w:fldChar")
        end.set(qn("w:fldCharType"), "end")
        for el in (begin, instr, sep, txt, end):
            run._r.append(el)

    def _header_footer(self, doc: Document, data: DocumentInput) -> None:
        section = doc.sections[0]
        section.orientation = WD_ORIENT.PORTRAIT
        section.left_margin = section.right_margin = Cm(2.2)
        section.top_margin = section.bottom_margin = Cm(2.0)
        section.different_first_page_header_footer = True  # clean cover page

        hp = section.header.paragraphs[0]
        hp.text = f"{self._s.company_name}  |  {data.narrative.proposal_title}  |  v{data.document_version}"
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for r in hp.runs:
            r.font.size = Pt(8)
            r.font.color.rgb = self._color("666666")

        fp = section.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = fp.add_run(f"{self._s.footer_text}  —  Page ")
        run.font.size = Pt(8)
        self._field(fp, "PAGE")
        r2 = fp.add_run(" of ")
        r2.font.size = Pt(8)
        self._field(fp, "NUMPAGES")

    def _table(self, doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> None:
        table = doc.add_table(rows=1, cols=len(headers))
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        hdr = table.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].text = ""
            p = hdr[i].paragraphs[0]
            run = p.add_run(h)
            run.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), self._s.primary_color.strip("#"))
            hdr[i]._tc.get_or_add_tcPr().append(shd)
        # repeat header row on page breaks
        trPr = table.rows[0]._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        trPr.append(th)
        for ridx, row in enumerate(rows):
            cells = table.add_row().cells
            for i, value in enumerate(row):
                cells[i].text = ""
                run = cells[i].paragraphs[0].add_run(value)
                run.font.size = Pt(9)
                if ridx % 2 == 1:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:color"), "auto")
                    shd.set(qn("w:fill"), "F2F5F9")
                    cells[i]._tc.get_or_add_tcPr().append(shd)
        if widths:
            for row in table.rows:
                for i, w in enumerate(widths):
                    row.cells[i].width = Cm(w)
        doc.add_paragraph()

    @staticmethod
    def _bullets(doc: Document, items: list[str], empty: str = "None identified.") -> None:
        if not items:
            doc.add_paragraph(empty)
            return
        for item in items:
            doc.add_paragraph(item, style="List Bullet")

    @staticmethod
    def _para(doc: Document, text: str) -> None:
        for chunk in [c.strip() for c in (text or "").split("\n\n") if c.strip()]:
            doc.add_paragraph(chunk)

    # ---- document --------------------------------------------------------------------
    def _build(self, d: DocumentInput) -> Document:  # noqa: C901 - linear document assembly
        doc = Document()
        self._setup_styles(doc)
        self._header_footer(doc, d)
        req, tp, est, ap, nar = d.requirements, d.technical, d.estimate, d.approval, d.narrative
        cur = est.currency

        # 1. Cover page
        if self._s.logo_path and Path(self._s.logo_path).exists():
            doc.add_picture(str(self._s.logo_path), width=Cm(5))
        for _ in range(5):
            doc.add_paragraph()
        p = doc.add_paragraph()
        r = p.add_run(self._s.company_name.upper())
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = self._color(self._s.accent_color)
        p = doc.add_paragraph()
        r = p.add_run(nar.proposal_title)
        r.font.size = Pt(28)
        r.font.bold = True
        r.font.color.rgb = self._color(self._s.primary_color)
        p = doc.add_paragraph()
        r = p.add_run("Technical-Functional Proposal")
        r.font.size = Pt(14)
        r.font.color.rgb = self._color("555555")
        doc.add_paragraph()
        cover_rows = [
            ["Customer", d.customer_name or req.customer_name or "—"],
            ["Proposal ID", d.proposal_id],
            ["Document version", str(d.document_version)],
            ["Date", utcnow().strftime("%d %B %Y")],
            ["Status", "Approved estimate" if ap and ap.status == ApprovalStatus.APPROVED else "Draft"],
            ["Artifact versions", f"Requirements v{req.version} · Technical v{tp.version} · Estimate v{est.version}"],
        ]
        self._table(doc, ["Item", "Detail"], cover_rows, widths=[4.5, 11.5])
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

        # 2. Executive summary
        doc.add_heading("1. Executive summary", level=1)
        self._para(doc, nar.executive_summary)
        self._table(
            doc,
            ["Total investment", "Total effort", "Estimated duration", "Confidence"],
            [[_money(est.total_cost, cur), f"{_hours(est.total_hours)} h", est.estimated_duration or "—", est.confidence_level.value.title()]],
        )

        # 3. Business context
        doc.add_heading("2. Business context and objectives", level=1)
        self._para(doc, nar.context_introduction)
        doc.add_heading("2.1 Context", level=2)
        self._para(doc, req.context or "—")
        doc.add_heading("2.2 Business problem", level=2)
        self._para(doc, req.problem_need or "—")
        doc.add_heading("2.3 Objectives", level=2)
        self._bullets(doc, req.objectives)
        doc.add_heading("2.4 Expected outcomes", level=2)
        self._bullets(doc, req.expected_results)
        if req.stakeholders:
            doc.add_heading("2.5 Stakeholders", level=2)
            self._table(doc, ["Stakeholder", "Interest"], [[s.name, s.interest] for s in req.stakeholders])

        # 4. Scope and requirements
        doc.add_heading("3. Scope and requirements", level=1)
        doc.add_heading("3.1 Functional requirements", level=2)
        self._table(
            doc,
            ["ID", "Requirement", "Priority", "Source"],
            [[r.id, r.description, r.priority, r.source] for r in req.functional_requirements],
            widths=[1.8, 10, 2, 2.2],
        )
        if req.non_functional_requirements:
            doc.add_heading("3.2 Non-functional requirements", level=2)
            self._table(
                doc,
                ["ID", "Requirement", "Priority", "Source"],
                [[r.id, r.description, r.priority, r.source] for r in req.non_functional_requirements],
                widths=[1.8, 10, 2, 2.2],
            )
        if req.business_rules:
            doc.add_heading("3.3 Business rules", level=2)
            self._bullets(doc, req.business_rules)
        vol = req.data_and_volumetrics
        if vol.data_sources or vol.data_volumes or vol.transaction_volumes:
            doc.add_heading("3.4 Data and volumetrics", level=2)
            self._table(
                doc,
                ["Aspect", "Detail"],
                [
                    ["Data sources", ", ".join(vol.data_sources) or "—"],
                    ["Data volumes", vol.data_volumes or "—"],
                    ["Transaction volumes", vol.transaction_volumes or "—"],
                    ["Growth", vol.growth_expectations or "—"],
                ],
            )
        doc.add_heading("3.5 In scope", level=2)
        self._bullets(doc, tp.scope or req.scope.included)

        # 5-7. Solution
        doc.add_heading("4. Proposed technical solution", level=1)
        self._para(doc, nar.solution_introduction)
        doc.add_heading("4.1 Solution overview", level=2)
        self._para(doc, tp.solution_overview)
        doc.add_heading("4.2 Architecture", level=2)
        self._para(doc, tp.architecture)
        if tp.architecture_components:
            doc.add_heading("4.3 Architecture components", level=2)
            self._table(
                doc,
                ["Component", "Type", "Responsibility", "Technology"],
                [[c.name, c.name, c.responsibility, c.technology] for c in tp.architecture_components],
            )
        if tp.technology_decisions:
            doc.add_heading("4.4 Technology stack", level=2)
            self._table(
                doc,
                ["Layer", "Technology", "Rationale", "Documented"],
                [[t.decision, t.decision, t.rationale, "Recommendation"] for t in tp.technology_decisions],
            )
        if tp.integrations:
            doc.add_heading("4.5 Integrations", level=2)
            self._table(
                doc,
                ["Integration", "Systems", "Pattern", "Protocol", "Notes"],
                [[i.name, ", ".join(i.name), i.name, i.mechanism, i.purpose] for i in tp.integrations],
            )
        if tp.requirements_traceability:
            doc.add_heading("4.6 Requirements traceability", level=2)
            self._table(
                doc,
                ["Requirement", "Covered by", "Notes"],
                [[t.requirement_id, ", ".join(t.covered_by), t.notes] for t in tp.requirements_traceability],
            )

        # 8-9. Delivery
        doc.add_heading("5. Implementation approach", level=1)
        self._para(doc, nar.delivery_introduction)
        acts_by_phase: dict[str, list] = {}
        for a in tp.phase_activities:
            acts_by_phase.setdefault(a.phase_id, []).append(a)
        dels_by_phase: dict[str, list] = {}
        for dl in tp.deliverables:
            dels_by_phase.setdefault(dl.phase_id, []).append(dl)
        criteria: dict[str, list[str]] = {}
        for c in tp.acceptance_criteria:
            criteria.setdefault(c.deliverable_id, []).append(c.description)
        for ph in sorted(tp.implementation_phases, key=lambda p: p.order):
            doc.add_heading(f"5.{ph.order} {ph.name} ({ph.duration_weeks:g} weeks)", level=2)
            self._para(doc, ph.objective)
            if ph.depends_on:
                doc.add_paragraph(f"Depends on: {', '.join(ph.depends_on)}")
            acts = acts_by_phase.get(ph.id, [])
            if acts:
                doc.add_heading("Activities", level=3)
                self._table(
                    doc,
                    ["ID", "Activity", "Tasks", "Profiles"],
                    [[a.id, f"{a.name}\n{a.description}".strip(), "\n".join(f"• {t}" for t in a.tasks), ", ".join(a.profile_ids)] for a in acts],
                    widths=[1.6, 5.4, 6.5, 2.5],
                )
            dels = dels_by_phase.get(ph.id, [])
            if dels:
                doc.add_heading("Deliverables and acceptance criteria", level=3)
                self._table(
                    doc,
                    ["Deliverable", "Description", "Acceptance criteria"],
                    [[f"{dl.id} {dl.name}", dl.description, "\n".join(f"• {c}" for c in criteria.get(dl.id, [])) or "—"] for dl in dels],
                )

        # 10. Profiles
        doc.add_heading("6. Required professional profiles", level=1)
        self._table(
            doc,
            ["Profile", "Seniority", "Responsibilities"],
            [[f"{p.role_title} ({p.role_id})", p.seniority, "\n".join(f"• {x}" for x in p.responsibilities)] for p in tp.required_profiles],
        )

        # 11. Duration
        doc.add_heading("7. Duration and milestones", level=1)
        if tp.timeline_estimation:
            doc.add_paragraph(f"Estimated total duration: {tp.timeline_estimation.total_duration_weeks:g} weeks. {tp.timeline_estimation.summary}".strip())
        if tp.milestones:
            self._table(doc, ["Milestone", "Phase", "Target week"], [[m.name, m.phase_id, f"{m.target_week:g}"] for m in tp.milestones])

        # 12-13
        doc.add_heading("8. Prerequisites and customer responsibilities", level=1)
        self._bullets(doc, tp.prerequisites)
        doc.add_heading("9. Dependencies, assumptions and constraints", level=1)
        doc.add_heading("9.1 Dependencies", level=2)
        self._bullets(doc, list(dict.fromkeys(tp.dependencies + req.dependencies)))
        doc.add_heading("9.2 Assumptions", level=2)
        self._bullets(doc, list(dict.fromkeys(tp.assumptions + req.assumptions)))
        doc.add_heading("9.3 Constraints", level=2)
        self._bullets(doc, list(dict.fromkeys(tp.constraints + req.constraints)))

        # 14. Risks
        doc.add_heading("10. Risks and mitigation", level=1)
        self._table(
            doc,
            ["Category", "Risk", "Probability", "Impact", "Mitigation"],
            [[r.category, r.description, r.probability, r.impact, r.mitigation] for r in tp.technical_risks],
        )

        # 15. Out of scope
        doc.add_heading("11. Out of scope", level=1)
        self._bullets(doc, list(dict.fromkeys(tp.out_of_scope + req.scope.excluded)))

        # 16-18. Financial
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        doc.add_heading("12. Financial proposal", level=1)
        self._para(doc, nar.financial_introduction)
        doc.add_heading("12.1 Financial summary", level=2)
        summary_rows = [["Subtotal (professional services)", _money(est.subtotal, cur)]]
        for adj in (est.contingency, est.discount, est.taxes):
            if adj and adj.applied:
                sign = "−" if adj is est.discount else ""
                summary_rows.append([f"{adj.label} ({_pct(adj.rate)})", f"{sign}{_money(adj.amount, cur)}"])
        summary_rows.append(["Total", _money(est.total_cost, cur)])
        self._table(doc, ["Concept", "Amount"], summary_rows, widths=[10, 6])
        doc.add_paragraph(f"Calculation method: {est.formula}").runs[0].font.size = Pt(8.5)

        doc.add_heading("12.2 Cost by phase", level=2)
        self._table(
            doc,
            ["Phase", "Hours", "Amount"],
            [[p.phase_name, _hours(p.hours), _money(p.amount, cur)] for p in est.phase_estimates],
        )
        doc.add_heading("12.3 Cost by profile", level=2)
        self._table(
            doc,
            ["Profile", "Hours", "Hourly rate", "Amount"],
            [[p.profile_name, _hours(p.hours), _money(p.hourly_rate, cur), _money(p.amount, cur)] for p in est.profile_estimates],
        )
        doc.add_heading("12.4 Commercial assumptions and exclusions", level=2)
        doc.add_paragraph("Commercial assumptions:")
        self._bullets(doc, est.commercial_assumptions)
        tax_note = (
            f"{est.taxes.label} applied at {_pct(est.taxes.rate)}." if est.taxes and est.taxes.applied
            else "Taxes are not included in the amounts above unless stated."
        )
        doc.add_paragraph(tax_note)
        doc.add_paragraph("Exclusions:")
        self._bullets(doc, est.exclusions)

        # 19. Approval
        doc.add_heading("13. Approval", level=1)
        if ap:
            self._table(
                doc,
                ["Field", "Value"],
                [
                    ["Decision", ap.status.value.replace("_", " ").title()],
                    ["Approved by", ap.user_id],
                    ["Approved at (UTC)", ap.decided_at.strftime("%Y-%m-%d %H:%M")],
                    ["Estimate version", str(ap.estimate_version)],
                    ["Technical proposal version", str(ap.technical_version)],
                    ["Estimate fingerprint", ap.estimate_fingerprint[:16] + "…"],
                    ["Feedback", ap.feedback or "—"],
                ],
                widths=[5, 11],
            )

        # 20. References
        doc.add_heading("14. Technical documentation references", level=1)
        if tp.documentation_sources:
            for ref in tp.documentation_sources:
                p = doc.add_paragraph(style="List Bullet")
                p.add_run(ref.title).bold = True
                p.add_run(f" — {ref.url}")
                if ref.relevance:
                    p.add_run(f" ({ref.relevance})")
        else:
            doc.add_paragraph(f"No documentation references recorded.".strip())

        # 21. Appendix
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        doc.add_heading("Appendix A. Detailed cost breakdown", level=1)
        self._table(
            doc,
            ["Phase", "Activity", "Profile", "Hours", "Rate", "Amount"],
            [
                [li.phase_name, f"{li.activity_id} {li.activity_name}", li.profile_name, _hours(li.hours), _money(li.hourly_rate, cur), _money(li.amount, cur)]
                for li in est.activity_estimates
            ],
        )
        if tp.open_questions:
            doc.add_heading("Appendix B. Open technical decisions", level=1)
            self._bullets(doc, [q.question for q in tp.open_questions])
        if nar.closing_statement:
            doc.add_heading("Closing", level=1)
            self._para(doc, nar.closing_statement)
        return doc
