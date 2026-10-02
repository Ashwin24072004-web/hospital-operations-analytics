from datetime import date
import pandas as pd
import plotly.express as px
import psycopg
import streamlit as st

from src.analytics import filter_options, metric, report
from src.chatbot import ChatResult, ChatbotError, answer_question
from src.config import groq_api_key
from src.query_catalog import get_query, load_catalog


st.set_page_config(
    page_title="Hospital Operations Analytics",
    page_icon="🏥",
    layout="wide",
)


@st.cache_data(ttl=300)
def cached_options():
    return filter_options()


@st.cache_data(ttl=120)
def cached_metric(query_id: str, start_date: date, end_date: date):
    return metric(query_id, start_date, end_date)


@st.cache_data(ttl=120)
def cached_report(query_id: str, start_date: date, end_date: date, **filters):
    return report(query_id, start_date, end_date, **filters)


def money(value) -> str:
    return f"₹{float(value or 0):,.0f}"


def render_overview(start_date: date, end_date: date) -> None:
    st.header("Hospital overview")
    st.caption("A management view of fictional hospital activity and collected payments.")
    columns = st.columns(4)
    columns[0].metric("Registered patients", f"{cached_metric('total_patients', start_date, end_date):,}")
    columns[1].metric("Doctors", f"{cached_metric('total_doctors', start_date, end_date):,}")
    columns[2].metric("Appointments", f"{cached_metric('total_appointments', start_date, end_date):,}")
    columns[3].metric("Collected revenue", money(cached_metric("total_revenue", start_date, end_date)))

    monthly = cached_report("monthly_appointments", start_date, end_date)
    status = cached_report("appointment_status", start_date, end_date)
    department = cached_report("department_activity", start_date, end_date)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.line(monthly, x="month", y="appointment_count", markers=True, title="Monthly appointments"),
            width="stretch",
        )
    with right:
        st.plotly_chart(
            px.pie(status, names="status", values="appointment_count", hole=0.45, title="Appointment status"),
            width="stretch",
        )
    st.plotly_chart(
        px.bar(
            department,
            x="department_name",
            y="appointment_count",
            title="Appointments by department",
            labels={"department_name": "Department", "appointment_count": "Appointments"},
        ),
        width="stretch",
    )
    st.subheader("Recent appointments")
    st.dataframe(cached_report("recent_appointments", start_date, end_date), width="stretch", hide_index=True)


def render_departments(start_date: date, end_date: date, options) -> None:
    st.header("Department analysis")
    departments = options["departments"]
    names = ["All departments", *departments["department_name"].tolist()]
    selected = st.selectbox("Department", names)
    department_id = None
    if selected != "All departments":
        department_id = int(departments.loc[departments["department_name"] == selected, "department_id"].iloc[0])
    frame = cached_report(
        "department_summary", start_date, end_date, department_id=department_id
    )
    if frame.empty:
        st.info("No department activity exists for the selected filters.")
        return
    st.dataframe(frame, width="stretch", hide_index=True)
    chart = frame.copy()
    chart["revenue"] = chart["revenue"].astype(float)
    st.plotly_chart(
        px.bar(chart, x="department_name", y="appointment_count", color="revenue", title="Workload and collected revenue"),
        width="stretch",
    )


def render_doctors(start_date: date, end_date: date, options) -> None:
    st.header("Doctor analysis")
    departments = options["departments"]
    department_names = ["All departments", *departments["department_name"].tolist()]
    chosen_department = st.selectbox("Department", department_names, key="doctor_department")
    department_id = None
    if chosen_department != "All departments":
        department_id = int(
            departments.loc[departments["department_name"] == chosen_department, "department_id"].iloc[0]
        )

    doctors = options["doctors"]
    if department_id is not None:
        doctors = doctors[doctors["department_id"] == department_id]
    doctor_names = ["All doctors", *doctors["doctor_name"].tolist()]
    chosen_doctor = st.selectbox("Doctor", doctor_names)
    doctor_id = None
    if chosen_doctor != "All doctors":
        doctor_id = int(doctors.loc[doctors["doctor_name"] == chosen_doctor, "doctor_id"].iloc[0])

    frame = cached_report(
        "doctor_summary",
        start_date,
        end_date,
        department_id=department_id,
        doctor_id=doctor_id,
    )
    st.dataframe(frame, width="stretch", hide_index=True)
    if not frame.empty:
        st.plotly_chart(
            px.bar(frame, x="doctor_name", y="appointment_count", color="department_name", title="Doctor workload"),
            width="stretch",
        )


def render_patients(start_date: date, end_date: date, options) -> None:
    st.header("Patient analysis")
    st.caption("All displayed names and records are generated and fictional.")
    city_values = ["All cities", *options["cities"]["city"].tolist()]
    city_choice = st.selectbox("City", city_values)
    search = st.text_input("Patient name contains", max_chars=50).strip()
    city = None if city_choice == "All cities" else city_choice
    frame = cached_report(
        "patient_summary",
        start_date,
        end_date,
        city=city,
        patient_search=search,
        patient_pattern=f"%{search}%",
    )
    st.dataframe(frame, width="stretch", hide_index=True)
    if frame.empty:
        st.info("No patients match the selected filters.")
        return
    patient_labels = {
        f"{row.patient_name} (ID {row.patient_id})": int(row.patient_id)
        for row in frame.itertuples()
    }
    selected_patient = st.selectbox("View patient history", list(patient_labels))
    history = cached_report(
        "patient_history",
        start_date,
        end_date,
        patient_id=patient_labels[selected_patient],
    )
    st.subheader("Visit history")
    if history.empty:
        st.info("This patient has no appointments in the selected period.")
    else:
        st.dataframe(history, width="stretch", hide_index=True)


def render_sql_showcase(start_date: date, end_date: date) -> None:
    st.header("SQL showcase")
    st.caption("Explore reviewed queries that can later become tools for a RAG chatbot.")
    allowed = [
        "total_revenue",
        "monthly_appointments",
        "appointment_status",
        "department_activity",
        "recent_appointments",
        "patients_without_appointments",
    ]
    catalog = load_catalog()
    label_to_id = {catalog[item].title: item for item in allowed}
    selected_label = st.selectbox("Business question", list(label_to_id))
    query = get_query(label_to_id[selected_label])
    st.markdown(f"**Question:** {query.question}")
    st.markdown(f"**Join approach:** {query.join_type} — {query.explanation}")
    with st.expander("View SQL"):
        st.code(query.sql, language="sql")
    result = cached_report(query.query_id, start_date, end_date)
    st.dataframe(result, width="stretch", hide_index=True)


def _render_chat_result(result: dict) -> None:
    st.markdown(result["answer"])
    details = []
    if result.get("source_title"):
        details.append(f"Source: {result['source_title']}")
    if result.get("model_used"):
        details.append(f"Model: {result['model_used']}")
    if details:
        st.caption(" · ".join(details))
    if result.get("source_title"):
        with st.expander("Trusted source"):
            st.write(f"**Source:** {result['source_title']}")
            if result.get("filters"):
                st.write("**Filters:**")
                st.json(result["filters"])
            if result.get("query_id"):
                query = get_query(result["query_id"])
                st.write(f"**Query ID:** `{query.query_id}`")
                st.write(f"**SQL approach:** {query.join_type} — {query.explanation}")
            if result.get("row_count"):
                st.write(f"**Matching rows:** {result['row_count']}")
    if result.get("rows"):
        with st.expander("View result data"):
            st.dataframe(pd.DataFrame(result["rows"]), width="stretch", hide_index=True)


def render_ai_assistant(start_date: date, end_date: date) -> None:
    st.header("AI Assistant")
    st.caption(
        "Ask about the synthetic hospital reports or metric definitions. "
        "The assistant can only run reviewed, read-only SQL queries."
    )
    st.info("Educational demo: every patient and event is fictional. Do not use this assistant for medical advice.")

    if not groq_api_key():
        st.warning("The AI Assistant needs a newly generated Groq API key. Other dashboard pages still work normally.")
        st.code(
            "GROQ_API_KEY=replace_with_your_rotated_key\n"
            "GROQ_PRIMARY_MODEL=openai/gpt-oss-120b\n"
            "GROQ_FALLBACK_MODEL=openai/gpt-oss-20b",
            language="text",
        )
        st.caption("Add these values to `.env`, then restart Streamlit. Never commit `.env`.")
        return

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    top_left, top_right = st.columns([4, 1])
    with top_left:
        st.caption(f"Active date range: {start_date.isoformat()} to {end_date.isoformat()}")
    with top_right:
        if st.button("Clear conversation", width="stretch"):
            st.session_state.chat_messages = []
            st.rerun()

    suggested_prompt = None
    if not st.session_state.chat_messages:
        st.write("**Try an example:**")
        suggestions = [
            "Which department has the most appointments?",
            "How many appointments were no-shows?",
            "Compare doctor workloads.",
            "What does collected revenue mean?",
        ]
        suggestion_columns = st.columns(2)
        for index, suggestion in enumerate(suggestions):
            with suggestion_columns[index % 2]:
                if st.button(suggestion, key=f"suggestion_{index}", width="stretch"):
                    suggested_prompt = suggestion

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("result"):
                _render_chat_result(message["result"])
            else:
                st.markdown(message["content"])

    typed_prompt = st.chat_input("Ask about hospital operations...")
    prompt = suggested_prompt or typed_prompt
    if not prompt:
        return

    previous_conversation = [
        {"role": item["role"], "content": item["content"]}
        for item in st.session_state.chat_messages[-6:]
    ]
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    try:
        with st.spinner("Checking trusted reports..."):
            result = answer_question(
                prompt,
                start_date,
                end_date,
                previous_conversation,
            )
    except ChatbotError as error:
        result = ChatResult(
            answer=str(error),
            intent="error",
            query_id=None,
            source_title="Groq service",
            filters={},
            rows=[],
            row_count=0,
            model_used="",
            needs_clarification=False,
        )
    st.session_state.chat_messages.append(
        {"role": "assistant", "content": result.answer, "result": result.to_dict()}
    )
    st.rerun()


def main() -> None:
    st.title("🏥 Hospital Operations Analytics")
    st.caption("PostgreSQL + joins + Streamlit · 100% synthetic portfolio data")
    try:
        options = cached_options()
    except psycopg.OperationalError:
        st.error("Cannot connect to PostgreSQL. Start Docker and load the database using the README instructions.")
        st.code("docker compose up -d --wait\npython scripts/generate_data.py\npython scripts/setup_database.py")
        st.stop()

    date_row = options["dates"].iloc[0]
    min_date = pd.to_datetime(date_row["min_date"]).date()
    max_date = pd.to_datetime(date_row["max_date"]).date()

    with st.sidebar:
        st.header("Controls")
        page = st.radio(
            "Page",
            ["Overview", "Departments", "Doctors", "Patients", "SQL showcase", "AI Assistant"],
        )
        selected_dates = st.date_input(
            "Appointment date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        st.divider()
        st.caption("Educational project. No real patient data.")

    if not isinstance(selected_dates, (tuple, list)) or len(selected_dates) != 2:
        st.warning("Select both a start and end date.")
        st.stop()
    start_date, end_date = selected_dates
    if start_date > end_date:
        st.warning("Start date must be before end date.")
        st.stop()

    renderers = {
        "Overview": lambda: render_overview(start_date, end_date),
        "Departments": lambda: render_departments(start_date, end_date, options),
        "Doctors": lambda: render_doctors(start_date, end_date, options),
        "Patients": lambda: render_patients(start_date, end_date, options),
        "SQL showcase": lambda: render_sql_showcase(start_date, end_date),
        "AI Assistant": lambda: render_ai_assistant(start_date, end_date),
    }
    renderers[page]()


if __name__ == "__main__":
    main()
