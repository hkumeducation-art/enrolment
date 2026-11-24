import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Course Enrolment Portal")

# --- UPDATED HEADING AND TEXT ---
st.title("Pre-enrolment for GS students before official enrolment period")
st.markdown("""
Please select a maximum of 4 electives. Please do not choose 2 courses scheduled for the same day.

[No resubmission is allowed. Please check your selection carefully before clicking to submit]

**[Important: You are required to enrol in the remaining 3 electives during the official enrolment period]**
""")
st.divider()

# --- CONFIGURATION ---
SHEETDB_URL = "https://sheetdb.io/api/v1/86bwjqyllhqzy"

# The exact 30 student numbers allowed
VALID_STUDENTS = [
    "30360001", "30360002", "30360003", "30360004", "30360005",
    "30360006", "30360007", "30360008", "30360009", "30360010",
    "30360011", "30360012", "30360013", "30360014", "30360015",
    "30360016", "30360017", "30360018", "30360019", "30360020",
    "30360021", "30360022", "30360023", "30360024", "30360025",
    "30360026", "30360027", "30360028", "30360029", "30360030"
]

# Updated Course Dictionary Grouped by Semester and Day
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

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_id = ""
    st.session_state.has_submitted = False

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.subheader("Student Login")
    student_id = st.text_input("Enter your Student Number:").strip()

    if st.button("Access Portal"):
        if student_id in VALID_STUDENTS:
            with st.spinner("Checking database..."):
                try:
                    # Look at Google Sheet to see who has submitted
                    all_records = requests.get(SHEETDB_URL).json()

                    # Extract all student numbers that are already in the sheet
                    existing_students = [record.get("Student Number", "") for record in all_records if isinstance(record, dict)]

                    if student_id in existing_students:
                        st.error("❌ You have already submitted your enrolment. Multiple submissions are not allowed.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.student_id = student_id
                        st.rerun()
                except Exception as e:
                    st.error("Failed to connect to the database. Please try again.")
        else:
            st.error("Access Denied. Invalid Student Number.")

# --- ENROLMENT SCREEN ---
else:
    st.success(f"Welcome, Student {st.session_state.student_id}!")

    # If they just submitted, hide the form and show success message
    if st.session_state.has_submitted:
        st.info("✅ Your enrolment has been successfully recorded. You may now close this window.")

    # Otherwise, show the checkboxes
    else:
        selected_courses_with_day = []

        for day, courses in SCHEDULE.items():
            st.subheader(f"📅 {day}")
            for course in courses:
                # FIX: We put the 'day' and 'course' together in the key so it is always 100% unique!
                if st.checkbox(course, key=f"{day}_{course}"):
                    selected_courses_with_day.append((day, course))

        st.divider()

        if st.button("Submit Enrolment"):
            total_selected = len(selected_courses_with_day)

            day_counts = {}
            for day, course in selected_courses_with_day:
                day_counts[day] = day_counts.get(day, 0) + 1

            conflict_days = [day for day, count in day_counts.items() if count > 1]

            if total_selected == 0:
                st.warning("Please select at least 1 course before submitting.")

            elif total_selected > 4:
                st.error(f"⚠️ You selected {total_selected} courses. You can only choose a maximum of 4.")

            elif conflict_days:
                days_str = ", ".join(conflict_days)
                st.error(f"⚠️ Schedule Conflict! You selected multiple courses on: **{days_str}**. Please choose only 1 course per time slot.")

            else:
                with st.spinner("Saving your enrolment..."):
                    final_courses = [item[1] for item in selected_courses_with_day]

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
                        # Success! Mark as submitted and refresh the page to hide the form
                        st.session_state.has_submitted = True
                        st.rerun()
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
