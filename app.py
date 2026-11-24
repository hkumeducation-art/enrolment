import streamlit as st
import requests
from datetime import datetime
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Course Enrolment Portal")

# --- UPDATED HEADING AND TEXT ---
st.title("Selection of electives for pre-enrolment")
st.markdown("""
1. Please select a maximum of **4 electives**. Do not choose 2 courses scheduled for the same day.
2. **No resubmission is allowed**. Please check your selections carefully before clicking to submit.
3. You are required to enrol in the remaining 3 electives during the official enrolment period, either this year, or next year (i.e. Year 2 for part-time students).
""")
st.divider()

# --- CONFIGURATION ---
SHEETDB_URL = "https://sheetdb.io/api/v1/86bwjqyllhqzy"

VALID_STUDENTS = [
    "30360001", "30360002", "30360003", "30360004", "30360005",
    "30360006", "30360007", "30360008", "30360009", "30360010",
    "30360011", "30360012", "30360013", "30360014", "30360015",
    "30360016", "30360017", "30360018", "30360019", "30360020",
    "30360021", "30360022", "30360023", "30360024", "30360025",
    "30360026", "30360027", "30360028", "30360029", "30360030"
]

SCHEDULE = {
    "Semester 1 Mondays": [
        "MEDD6609 - Digital Technology and Educational leadership",
        "MEDD7117 - Drama Appreciation and Teaching",
        "MEDD8666 - Abnormal Psychology and Positive Psychology",
        "MEDD8678 - Counselling Process, Ethics and Skills"
    ],
    "Semester 1 Tuesdays": [
        "MEDD8679 - Counselling Assessment and Interventions",
        "MEDD8801 - Classical Chinese Language and the Reading of Classical Texts",
        "MEDD8802 - Sociology of Education: Classic and Contemporary Theories ",
        "MEDD8815(A) (ARM) - Introduction to Statistical Methods"
    ],
    "Semester 1 Wednesdays": [
        "MEDD8815(B) (ARM) - Introduction to Statistical Methods",
        "MEDD8829 - Effective Strategies for Learning and Teaching in Small Class Environment for Primary Education",
        "MEDD8831 - Nurturing Creativity: Theories and Practices",
        "MEDD8836 - Personal Growth of Teachers and Guidance Personnel"
    ],
    "Semester 1 Thursdays": [
        "MEDD8877 - Social and Emotional Needs of Gifted Individuals",
        "MEDD8881 - Learning Design and Technology"
    ],
    "Semester 1 Fridays": [
        "MEDD8884 - Career Counselling and Talent Development in Schools",
        "MEDD8886 (ARM) - Qualitative Methods: Research Design, Data Collection and Analysis",
        "MEDD8888 (ARM) - Methods for Evaluation Research in Education",
        "MEDD8889 - Strategic Leadership in School Administration and Management for Career Advancement "
    ],
    "Semester 2 Mondays": [
        "MEDD8888 (ARM) - Methods for Evaluation Research in Education",
        "MEDD8890 - Edu-Preneurial Leadership in Continuing Professional Development for Career Advancement",
        "MEDD8907 (ARM) - Statistical Analyses for Advancing Educational Equity and Social Justice ",
        "MEDD8908 (ARM) - Foundations of Qualitative Education Research: Concepts, Strategies and Methods",
        "MEDD8913 - Educational Leadership for Equity and Social Justice"
    ],
    "Semester 2 Tuesdays": [
        "MEDD8916 - Public Policy in Early Childhood and Primary Education",
        "MEDD8920 - Classroom Research in General Studies and Liberal Education",
        "MEDD8943 - Empowering Language Teaching with Technology, Learning, Assessment and Feedback Design",
        "MEDD8886 (ARM) - Qualitative Methods: Research Design, Data Collection and Analysis"
    ],
    "Semester 2 Wednesdays": [
        "MEDD8925 (ARM) - Analysing Textual and Documentary Data in Quantitative Research",
        "MEDD8926 (ARM) - Methods and Measurement in Comparative Research: Happiness, Well-Being, and Education",
        "MEDD8928 - Educational Change in a Global Era: Theories and Debates",
        "MEDD8931 - People-centric Design for Education Using Simulation Technology",
        "MEDD8933 (ARM) - Identifying Evidence-based Practices in School Settings: Experimental Research Method and Design"
    ],
    "Semester 2 Thursdays": [
        "MEDD8934 - Artificial Intelligence and Language Education",
        "MEDD8935 - Theories of Learning in STEM Education",
        "MEDD8939 (ARM) - Conducting, Analysing, and Reporting Interviews",
        "MEDD8940 (ARM) - Design-based Research for Educational Problem-solving",
        "MEDD8942 (ARM) - Interviews in Educational Research"
    ],
    "Semester 2 Fridays": [
        "MEDD8944 - Leading Curriculum in Context: An Introduction to Global Perspectives",
        "MEDD8945 - Leading Sustainable School-Community Relations",
        "MEDD8908 - Foundations of Qualitative Education Research: Concepts, Strategies and Methods"
    ]
}

# --- PDF GENERATOR FUNCTION ---
def create_pdf(student_id, courses_with_day):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Enrolment Receipt", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Student Number: {student_id}", ln=True)
    pdf.cell(0, 10, "-"*65, ln=True)
    
    for day, course in courses_with_day:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"{day}:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, f"  - {course}")
        pdf.ln(2)
        
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "-"*65, ln=True)
    pdf.cell(0, 10, f"Date & Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 10, "Please keep this summary for your records.", ln=True)
    
    # Save to a temporary file and read as bytes for download
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        with open(tmp.name, "rb") as f:
            return f.read()

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_id = ""
    st.session_state.step = "select" # States: 'select', 'review', 'submitted'
    st.session_state.selected_courses_with_day = []

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.subheader("Student Login")
    student_id = st.text_input("Enter your Student Number:").strip()

    if st.button("Access Portal"):
        if student_id in VALID_STUDENTS:
            with st.spinner("Checking database..."):
                try:
                    all_records = requests.get(SHEETDB_URL).json()
                    existing_students = [record.get("Student Number", "") for record in all_records if isinstance(record, dict)]

                    if student_id in existing_students:
                        st.error("❌ You have already submitted your enrolment. Multiple submissions are not allowed.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.student_id = student_id
                        st.rerun()
                except Exception:
                    st.error("Failed to connect to the database. Please try again.")
        else:
            st.error("Access Denied. Invalid Student Number.")

# --- ENROLMENT SCREEN ---
else:
    # -----------------------------------
    # STEP 1: SELECT COURSES
    # -----------------------------------
    if st.session_state.step == "select":
        st.success(f"Welcome, Student {st.session_state.student_id}!")
        current_selections = []

        for day, courses in SCHEDULE.items():
            st.subheader(f"📅 {day}")
            for course in courses:
                # Check if this course was previously selected so we can keep it ticked if they hit "Back"
                is_checked = any(c == course and d == day for d, c in st.session_state.selected_courses_with_day)
                
                if st.checkbox(course, value=is_checked, key=f"{day}_{course}"):
                    current_selections.append((day, course))

        st.divider()

        if st.button("Review Selections"):
            total_selected = len(current_selections)
            day_counts = {}
            for day, course in current_selections:
                day_counts[day] = day_counts.get(day, 0) + 1
                
            conflict_days = [day for day, count in day_counts.items() if count > 1]

            # Validations
            if total_selected == 0:
                st.warning("Please select at least 1 course before continuing.")
            elif total_selected > 4:
                st.error(f"⚠️ You selected {total_selected} courses. You can only choose a maximum of 4.")
            elif conflict_days:
                days_str = ", ".join(conflict_days)
                st.error(f"⚠️ Schedule Conflict! You selected multiple courses on: **{days_str}**. Please choose only 1 course per time slot.")
            else:
                # If valid, move to review step
                st.session_state.selected_courses_with_day = current_selections
                st.session_state.step = "review"
                st.rerun()

    # -----------------------------------
    # STEP 2: REVIEW SUMMARY
    # -----------------------------------
    elif st.session_state.step == "review":
        st.subheader("📝 Review Your Selections")
        st.write("Please review your courses carefully. **Your enrolment is not submitted yet!**")
        
        st.info(" \n".join([f"- **{day}**: {course}" for day, course in st.session_state.selected_courses_with_day]))
        
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⬅️ Back to Edit"):
                st.session_state.step = "select"
                st.rerun()
                
        with col2:
            if st.button("✅ Confirm & Submit"):
                with st.spinner("Saving your enrolment..."):
                    final_courses = [item[1] for item in st.session_state.selected_courses_with_day]
                    while len(final_courses) < 4:
                        final_courses.append("")

                    data = {
                        "data": [{
                            "Student Number": st.session_state.student_id,
                            "Course 1": final_courses[0],
                            "Course 2": final_courses[1],
                            "Course 3": final_courses[2],
                            "Course 4": final_courses[3],
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }]
                    }

                    response = requests.post(SHEETDB_URL, json=data)

                    if response.status_code == 201:
                        st.session_state.step = "submitted"
                        st.rerun()
                    else:
                        st.error("Something went wrong. Please try again.")

    # -----------------------------------
    # STEP 3: SUBMITTED (SUCCESS & PDF)
    # -----------------------------------
    elif st.session_state.step == "submitted":
        st.success("✅ **Success! Your enrolment has been officially recorded.**")
        st.write("You may download your official PDF receipt below, or close this window.")
        
        # Generate the PDF file
        pdf_bytes = create_pdf(st.session_state.student_id, st.session_state.selected_courses_with_day)
        
        st.download_button(
            label="💾 Download PDF Receipt",
            data=pdf_bytes,
            file_name=f"Enrolment_Receipt_{st.session_state.student_id}.pdf",
            mime="application/pdf"
        )
