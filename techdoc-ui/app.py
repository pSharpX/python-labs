import streamlit as st
import httpx

from settings import AppSettings
from src.client.proposal_client import ProposalAPIClient

settings = AppSettings()
api_client = ProposalAPIClient(settings)

st.set_page_config(
    page_title="AI Technical Proposal Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "proposal_id" not in st.session_state:
    st.session_state.proposal_id = None
if "current_proposal_data" not in st.session_state:
    st.session_state.current_proposal_data = None

# Sidebar - Proposal Management & Navigation
with st.sidebar:
    st.title("💼 Presales Assistant")
    st.markdown("---")

    if st.button("➕ New Proposal", use_container_width=True):
        st.session_state.messages = []
        st.session_state.proposal_id = None
        st.session_state.current_proposal_data = None
        st.rerun()

    if st.session_state.proposal_id:
        st.info(f"**Active ID:** {st.session_state.proposal_id}")
        if st.button("🔄 Refresh Data", use_container_width=True):
            data = api_client.get_proposal_full(st.session_state.proposal_id)
            st.session_state.current_proposal_data = data
            st.rerun()

# Main Workspace Header
st.title("Enterprise AI Technical Proposal Generator")
st.caption("Driven by LangGraph, FastAPI, and Automated Word Generation")

# Tabs Layout
tab_chat, tab_req, tab_tech, tab_fin, tab_doc = st.tabs(
    [
        "💬 Conversational Chat",
        "📋 Requirements Specification",
        "🏗️ Technical Architecture",
        "💰 Financial Estimate & Approval",
        "📄 Generated Document",
    ]
)

# TAB 1: Chat Interface
with tab_chat:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Describe your project or answer questions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("Processing workflow stage..."):
            try:
                if not st.session_state.proposal_id:
                    res = api_client.create_proposal(prompt)
                    st.session_state.proposal_id = res["proposal_id"]
                else:
                    res = api_client.send_message(
                        st.session_state.proposal_id, prompt
                    )

                # Update state snapshot
                full_data = api_client.get_proposal_full(
                    st.session_state.proposal_id
                )
                st.session_state.current_proposal_data = full_data

                response_text = f"**Stage:** {res['current_stage'].upper()} | **Approval:** {res['approval_status']}\n\n"
                if res.get("requirements_summary"):
                    response_text += f"**Requirements:** {res['requirements_summary']}\n\n"
                if res.get("technical_summary"):
                    response_text += f"**Architecture:** {res['technical_summary']}\n\n"
                if res.get("total_cost"):
                    response_text += f"**Calculated Total:** ${res['total_cost']:,.2f}\n"

                st.session_state.messages.append(
                    {"role": "assistant", "content": response_text}
                )
                with st.chat_message("assistant"):
                    st.write(response_text)
                st.rerun()

            except Exception as e:
                st.error(f"Failed to communicate with API: {e}")

# TAB 2: Requirements View
with tab_req:
    pdata = st.session_state.current_proposal_data
    if pdata and pdata.get("requirements"):
        req = pdata["requirements"]
        st.subheader("Requirements Specification")
        st.json(req)
    else:
        st.info("No validated requirements specification available yet.")

# TAB 3: Technical Proposal View
with tab_tech:
    pdata = st.session_state.current_proposal_data
    if pdata and pdata.get("technical_proposal"):
        tech = pdata["technical_proposal"]
        st.subheader(f"Service: {tech.get('requested_service')}")
        st.markdown(f"**Segment:** {tech.get('segment')} | **Line:** {tech.get('business_line')}")
        st.markdown("### Executive Summary")
        st.write(tech.get("executive_summary"))
        st.markdown("### Required Profiles")
        st.write(", ".join(tech.get("required_profiles", [])))
    else:
        st.info("No technical proposal generated yet.")

# TAB 4: Financial Estimate & Approval Panel
with tab_fin:
    pdata = st.session_state.current_proposal_data
    if pdata and pdata.get("financial_estimate"):
        fin = pdata["financial_estimate"]
        st.subheader("Financial Estimate & Effort Breakdown")

        col1, col2, col3 = st.columns(3)
        col1.metric("Subtotal", f"${fin.get('subtotal'):,.2f}")
        col2.metric("Taxes / Contingency", f"${fin.get('taxes') + fin.get('contingency'):,.2f}")
        col3.metric("Total Investment", f"${fin.get('total_cost'):,.2f}")

        st.markdown("### Human-In-The-Loop Decision")
        st.write(f"**Current Status:** {fin.get('approval_status')}")

        c_app, c_rej = st.columns(2)
        if c_app.button("✅ Approve Estimate", use_container_width=True):
            res = api_client.submit_approval(
                st.session_state.proposal_id, "approved"
            )
            st.success("Proposal approved! Generating Word document...")
            st.session_state.current_proposal_data = api_client.get_proposal_full(
                st.session_state.proposal_id
            )
            st.rerun()

        if c_rej.button("❌ Request Scope Changes", use_container_width=True):
            res = api_client.submit_approval(
                st.session_state.proposal_id, "changes_requested"
            )
            st.warning("Scope changes requested. Routing back to Requirements.")
            st.session_state.current_proposal_data = api_client.get_proposal_full(
                st.session_state.proposal_id
            )
            st.rerun()
    else:
        st.info("No financial estimate generated yet.")

# TAB 5: Word Document Download
with tab_doc:
    pdata = st.session_state.current_proposal_data
    if pdata and pdata.get("final_document"):
        doc_info = pdata["final_document"]
        st.success("🎉 Word Document generated and ready!")
        st.write(f"**Filename:** {doc_info.get('filename')}")
        st.write(f"**SHA256 Hash:** `{doc_info.get('content_hash')}`")

        download_url = api_client.get_document_download_url(
            st.session_state.proposal_id
        )
        try:
            file_bytes = httpx.get(download_url).content
            st.download_button(
                label="📥 Download Microsoft Word (.docx)",
                data=file_bytes,
                file_name=doc_info.get("filename"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Could not download document: {e}")
    else:
        st.info("Word document will be generated automatically once financial estimate is approved.")