import streamlit as st

from src.agent import run_agent, run_agent_followup

st.set_page_config(page_title="Mumzworld Gift Finder", layout="wide")

st.markdown(
    """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div.block-container {padding-top: 2rem; max-width: 980px;}
    label {font-weight: 600;}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Mumzworld AI Gift Finder")
st.caption("Bilingual gift recommendations for moms, babies, and kids.")

if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "pending_clarification" not in st.session_state:
    st.session_state.pending_clarification = False
if "original_query" not in st.session_state:
    st.session_state.original_query = ""
if "clarification_question_en" not in st.session_state:
    st.session_state.clarification_question_en = None
if "clarification_question_ar" not in st.session_state:
    st.session_state.clarification_question_ar = None


def render_result(result):
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**I understood:** {result.query_understood_en}")
    with col2:
        st.info(f"**فهمت:** {result.query_understood_ar}")

    if result.needs_clarification:
        st.warning(result.clarification_question_en)
        st.warning(result.clarification_question_ar)
        return

    if result.fallback_message_en:
        st.error(result.fallback_message_en)
        st.error(result.fallback_message_ar)
        return

    for i, product in enumerate(result.products):
        with st.expander(
            f"Option {i + 1}: {product.name_en} — {product.price_aed} AED",
            expanded=True,
        ):
            left, right = st.columns(2)
            with left:
                st.markdown(f"**{product.name_en}**")
                st.write(product.description_en)
                st.write(
                    f"Category: {product.category} | Age: {product.age_range}"
                )
                st.write(f"*{product.reasoning_en}*")
                st.progress(
                    product.confidence,
                    text=f"Confidence: {int(product.confidence * 100)}%",
                )
            with right:
                st.markdown(f"**{product.name_ar}**")
                st.write(product.description_ar)
                st.write(f"الفئة: {product.category} | العمر: {product.age_range}")
                st.write(f"*{product.reasoning_ar}*")


with st.form("gift_search"):
    user_input = st.text_input(
        "Describe what you're looking for",
        placeholder=(
            "e.g. thoughtful gift for a friend with a 6-month-old, under 200 AED"
        ),
    )
    submitted = st.form_submit_button("Find Gifts")

if submitted and user_input:
    with st.spinner("Finding the best gifts..."):
        result = run_agent(user_input)
    st.session_state.last_result = result
    st.session_state.original_query = user_input
    st.session_state.pending_clarification = result.needs_clarification
    st.session_state.clarification_question_en = result.clarification_question_en
    st.session_state.clarification_question_ar = result.clarification_question_ar

if st.session_state.last_result:
    render_result(st.session_state.last_result)

if st.session_state.pending_clarification:
    with st.form("clarification_form"):
        clarification_reply = st.text_input(
            "Answer the clarification question",
            key="clarification_reply",
        )
        clarification_submitted = st.form_submit_button("Submit")
    if clarification_submitted and clarification_reply:
        with st.spinner("Updating recommendations..."):
            followup_result = run_agent_followup(
                st.session_state.original_query,
                clarification_reply,
            )
        st.session_state.last_result = followup_result
        st.session_state.pending_clarification = followup_result.needs_clarification
        st.session_state.clarification_question_en = (
            followup_result.clarification_question_en
        )
        st.session_state.clarification_question_ar = (
            followup_result.clarification_question_ar
        )
