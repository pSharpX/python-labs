"""Deterministic financial calculations.

The LLM proposes effort (hours per activity and profile). This service is the only
place where money is computed. It:

* looks up hourly rates from the configured rate card (never guesses),
* checks that every profile is authorised by the technical proposal,
* applies contingency / discount / tax only when the rules enable them,
* rounds with ``Decimal`` according to configured rounding rules,
* re-verifies the arithmetic before the estimate can be approved.
"""

from __future__ import annotations

import decimal
import json
from collections import OrderedDict
from decimal import Decimal
from pathlib import Path
from typing import Protocol

from src.shared.enums import EstimateStatus, Confidence
from src.shared.models import RateCard, FinancialRules, PercentageRule, AdjustmentLine, EffortMappingDraft, \
    TechnicalProposal, FinancialEstimate, EstimateLineItem, ProfileEstimate, PhaseEstimate


class FinancialConfigError(RuntimeError):
    pass


class RateProvider(Protocol):
    def get_rate_card(self) -> RateCard: ...


class FileRateProvider:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def get_rate_card(self) -> RateCard:
        try:
            return RateCard.model_validate(json.loads(self._path.read_text(encoding="utf-8")))
        except FileNotFoundError as exc:
            raise FinancialConfigError(f"Rate card not found: {self._path.name}") from exc
        except (json.JSONDecodeError, ValueError) as exc:
            raise FinancialConfigError(f"Rate card is invalid: {self._path.name}") from exc


def load_financial_rules(path: Path) -> FinancialRules:
    try:
        return FinancialRules.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
    except FileNotFoundError as exc:
        raise FinancialConfigError(f"Financial rules file not found: {Path(path).name}") from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise FinancialConfigError(f"Financial rules file is invalid: {Path(path).name}") from exc


class FinancialService:
    def __init__(self, rate_provider: RateProvider, rules: FinancialRules) -> None:
        self._rates = rate_provider
        self._rules = rules

    @property
    def rules(self) -> FinancialRules:
        return self._rules

    def rate_card(self) -> RateCard:
        return self._rates.get_rate_card()

    # ---- rounding --------------------------------------------------------------------
    def _money(self, value: Decimal) -> Decimal:
        mode = getattr(decimal, self._rules.rounding.mode, decimal.ROUND_HALF_UP)
        return value.quantize(self._rules.rounding.quantum, rounding=mode)

    def _hours(self, value: Decimal) -> Decimal:
        q = self._rules.rounding.hours_quantum
        if q <= 0:
            return value
        # round to the nearest hours quantum (e.g. 0.5h)
        return ((value / q).quantize(Decimal("1"), rounding=decimal.ROUND_HALF_UP) * q).normalize()

    def _adjust(self, rule: PercentageRule, base: Decimal, default_label: str) -> AdjustmentLine:
        amount = self._money(base * rule.rate) if rule.enabled else Decimal("0.00")
        return AdjustmentLine(
            label=rule.label or default_label,
            rate=rule.rate if rule.enabled else Decimal("0"),
            base=self._money(base),
            amount=self._money(amount),
            applied=rule.enabled,
        )

    # ---- calculation -----------------------------------------------------------------
    def calculate(
        self,
        *,
        proposal_id: str,
        version: int,
        draft: EffortMappingDraft,
        technical: TechnicalProposal,
        technical_fingerprint: str,
        revision_feedback: str | None = None,
    ) -> FinancialEstimate:
        errors: list[str] = []
        warnings: list[str] = []
        rules = self._rules
        try:
            card = self.rate_card()
        except FinancialConfigError as exc:
            card = RateCard(currency=rules.currency, rates={})
            errors.append(str(exc))

        if card.currency != rules.currency:
            errors.append(f"Incompatibilidad de moneda: la lista de tarifas es {card.currency}, las reglas requieren {rules.currency}")

        phases = {p.id: p for p in technical.implementation_phases}
        activities = {a.id: a for a in technical.phase_activities}
        authorised = {p.role_id: p for p in technical.required_profiles}

        lines: list[EstimateLineItem] = []
        for item in draft.items:
            act = activities.get(item.activity_id)
            if act is None:
                errors.append(f"La estimación hace referencia a una actividad desconocida '{item.activity_id}'")
                continue
            prof = authorised.get(item.profile_id)
            if prof is None:
                errors.append(
                    f"El perfil '{item.profile_id}' en la actividad {item.activity_id} no está autorizado para este servicio"
                )
                continue
            try:
                hours = self._hours(Decimal(str(item.hours)))
            except decimal.InvalidOperation:
                errors.append(f"Invalid hours for {item.activity_id}/{item.profile_id}")
                continue
            if hours <= 0:
                errors.append(f"Hours must be positive for {item.activity_id}/{item.profile_id}")
                continue
            if hours > rules.max_hours_per_item:
                errors.append(
                    f"{hours}h for {item.activity_id}/{item.profile_id} exceeds the {rules.max_hours_per_item}h item limit"
                )
                continue
            rate = card.rates.get(item.profile_id)
            if rate is None:
                errors.append(f"No se ha configurado una tarifa por hora para el perfil '{item.profile_id}' ({prof.role_title})")
                continue
            if rate <= 0:
                errors.append(f"Tarifa por hora no válida para el perfil '{item.profile_id}'")
                continue
            phase = phases.get(act.phase_id)
            lines.append(
                EstimateLineItem(
                    phase_id=act.phase_id,
                    phase_name=phase.name if phase else act.phase_id,
                    activity_id=act.id,
                    activity_name=act.name,
                    profile_id=prof.role_id,
                    profile_name=prof.role_title,
                    hours=hours,
                    hourly_rate=self._money(rate),
                    amount=self._money(hours * rate),
                    rationale=item.rationale,
                    confidence=item.confidence,
                )
            )

        estimated_ids = {line.activity_id for line in lines}
        missing_acts = [a for a in activities if a not in estimated_ids]
        if missing_acts:
            msg = "Activities without effort: " + ", ".join(missing_acts)
            (errors if rules.require_all_activities_estimated else warnings).append(msg)
        for info in draft.missing_information:
            warnings.append(f"Missing information: {info}")

        # aggregate (ordered by first appearance)
        by_profile: OrderedDict[str, list[EstimateLineItem]] = OrderedDict()
        by_phase: OrderedDict[str, list[EstimateLineItem]] = OrderedDict()
        for line in lines:
            by_profile.setdefault(line.profile_id, []).append(line)
            by_phase.setdefault(line.phase_id, []).append(line)

        profile_estimates = [
            ProfileEstimate(
                profile_id=pid,
                profile_name=items[0].profile_name,
                hours=sum((i.hours for i in items), Decimal("0")),
                hourly_rate=items[0].hourly_rate,
                amount=self._money(sum((i.amount for i in items), Decimal("0"))),
            )
            for pid, items in by_profile.items()
        ]
        phase_order = {p.id: p.order for p in technical.implementation_phases}
        phase_estimates = sorted(
            [
                PhaseEstimate(
                    phase_id=ph,
                    phase_name=items[0].phase_name,
                    hours=sum((i.hours for i in items), Decimal("0")),
                    amount=self._money(sum((i.amount for i in items), Decimal("0"))),
                )
                for ph, items in by_phase.items()
            ],
            key=lambda p: phase_order.get(p.phase_id, 999),
        )

        subtotal = self._money(sum((line.amount for line in lines), Decimal("0")))
        contingency = self._adjust(rules.contingency, subtotal, "Contingency")
        discount = self._adjust(rules.discount, subtotal + contingency.amount, "Discount")
        taxable = subtotal + contingency.amount - discount.amount
        taxes = self._adjust(rules.tax, taxable, "Taxes")
        total = self._money(taxable + taxes.amount)

        duration = ""
        if technical.timeline_estimation:
            duration = f"{technical.timeline_estimation.total_duration_weeks:g} weeks"
            if technical.timeline_estimation.summary:
                duration += f" ({technical.timeline_estimation.summary})"

        estimate = FinancialEstimate(
            proposal_id=proposal_id,
            version=version,
            status=EstimateStatus.INVALID if errors else EstimateStatus.READY_FOR_APPROVAL,
            based_on_technical_fingerprint=technical_fingerprint,
            based_on_technical_version=technical.version,
            based_on_requirements_fingerprint=technical.based_on_requirements_fingerprint,
            currency=rules.currency,
            estimation_method=draft.estimation_method,
            formula=rules.formula_description,
            rate_card_source=f"{card.source} ({card.effective_date})".strip(),
            activity_estimates=lines,
            profile_estimates=profile_estimates,
            phase_estimates=phase_estimates,
            hours_by_profile={p.profile_id: p.hours for p in profile_estimates},
            total_hours=sum((line.hours for line in lines), Decimal("0")),
            subtotal=subtotal,
            contingency=contingency,
            discount=discount,
            taxes=taxes,
            total_cost=total,
            estimated_duration=duration,
            commercial_assumptions=draft.commercial_assumptions,
            exclusions=draft.exclusions,
            confidence_level=draft.confidence_level if not errors else Confidence.LOW,
            explanation=draft.explanation,
            validation_errors=errors,
            validation_warnings=warnings,
            revision_feedback=revision_feedback,
        )
        errors.extend(self.verify(estimate))
        if errors:
            estimate.validation_errors = list(dict.fromkeys(errors))
            estimate.status = EstimateStatus.INVALID
        return estimate

    def verify(self, est: FinancialEstimate) -> list[str]:
        """Independent arithmetic and consistency check of a computed estimate."""
        problems: list[str] = []
        for line in est.activity_estimates:
            if self._money(line.hours * line.hourly_rate) != line.amount:
                problems.append(f"Arithmetic mismatch on {line.activity_id}/{line.profile_id}")
        subtotal = self._money(sum((line.amount for line in est.activity_estimates), Decimal("0")))
        if subtotal != est.subtotal:
            problems.append("Subtotal does not equal the sum of line items")
        if sum((p.amount for p in est.phase_estimates), Decimal("0")) != sum(
            (p.amount for p in est.profile_estimates), Decimal("0")
        ):
            problems.append("Phase and profile totals disagree")
        adjustments = [a for a in (est.contingency, est.discount, est.taxes) if a]
        for adj in adjustments:
            if not adj.applied and adj.amount != 0:
                problems.append(f"{adj.label} applied although disabled")
        c = est.contingency.amount if est.contingency else Decimal("0")
        d = est.discount.amount if est.discount else Decimal("0")
        t = est.taxes.amount if est.taxes else Decimal("0")
        expected = self._money(est.subtotal + c - d + t)
        if expected != est.total_cost:
            problems.append("Total does not reconcile with subtotal and adjustments")
        if est.currency != self._rules.currency:
            problems.append("Estimate currency differs from configured currency")
        return problems
