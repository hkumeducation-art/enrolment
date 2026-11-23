import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Course Enrolment Portal")

# --- UPDATED HEADING AND TEXT ---
st.title("Pre-enrolment for GS students before official enrolment period")
st.markdown("Please select a maximum of 4 electives. Please do not choose more than 1 course scheduled for the same day. **[Important: You are required to enrol in the remaining 3 electives during the official enrolment period]**")
st.divider()

# --- CONFIGURATION ---
SHEETDB_URL = "https://sheetdb.io/api/v1/irwnfb4z2oayi"

# The exact 30 student numbers allowed
VALID_STUDENTS = [
    "30360000", "30361235", "30361264", "30361321", "30362111", 
    "30362154", "30362222", "30362323", "30363003", "30363333", 
    "30364251", "30364263", "30364444", "30364566", "30365262", 
    "30365478", "30365545", "30365555", "30365650", "30366425", 
    "30366666", "30367847", "30367878", "30367898", "30367899", 
    "30368798", "30369241", "30369812", "30369854", "30369999"
]

# Course Dictionary Grouped by Day
SCHEDULE = {
    "Mondays": [
        "MABC0001 - Intro to course 001",
        "MABC0002 - Intro to course 002",
        "MABC0003 - Intro to course 003 (ARM)",
        "MABC0004 - Intro to course 004",
        "MABC0005 - Intro to course 005",
        "MABC0006 - Intro to course 006",
        "MABC0007 - Intro to course 007",
        "MABC0008 - Intro to course 008"
    ],
    "Tuesdays": [
        "MABC0009 - Intro to course 009",
        "MABC0010 - Intro to course 010 (ARM)",
        "MABC0011 - Intro to course 011",
        "MABC0012 - Intro to course 012",
        "MABC0013 - Intro to course 013",
        "MABC0014 - Intro to course 014",
        "MABC0015 - Intro to course 015",
        "MABC0016 - Intro to course 016"
    ],
    "Wednesdays": [
        "MABC0017 - Intro to course 017",
        "MABC0018 - Intro to course 018",
        "MABC0019 - Intro to course 019",
        "MABC0020 - Intro to course 020 (ARM)",
        "MABC0021 - Intro to course 021",
        "MABC0022 - Intro to course 022",
        "MABC0023 - Intro to course 023",
        "MABC0024 - Intro to course 024"
    ],
    "Thursdays": [
        "MABC0025 - Intro to course 025",
        "MABC0026 - Intro to course 026",
        "MABC0027 - Intro to course 027",
        "MABC0028 - Intro to course 028",
        "MABC0029 - Intro to course 029",
        "MABC0030 - Intro to course 030 (ARM)",
        "MABC0031 - Intro to course 031",
        "MABC0032 - Intro to course 032"
    ],
    "Fridays": [
        "MABC0033 - Intro to course 033",
        "MABC0034 - Intro to course 034",
        "MABC0035 - Intro to course 035",
        "MABC0036 - Intro to course 036",
        "MABC0037 - Intro to course 037 (ARM)",
        "MABC0038 - Intro to course 038 (ARM)",
        "MABC0039 - Intro to course 039",
        "MABC0040 - Intro to course 040"
    ]
}

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_id = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.subheader("Student Login")
    student_id = st.text_input("Enter your Student Number:")
    
    if st.button("Access Portal"):
        if student_id in VALID_STUDENTS:
            st.session_state.logged_in = True
            st.session_state.student_id = student_id
            st.rerun()
        else:
            st.error("Access Denied. Invalid Student Number.")

# --- ENROLMENT SCREEN ---
else:
    st.success(f"Welcome, Student {st.session_state.student_id}!")
    
    # Create checkboxes and store selections
    selected_courses_with_day = []
    
    for day, courses in SCHEDULE.items():
        st.subheader(f"📅 {day}")
        for course in courses:
            # Create a checkbox for each course
            if st.checkbox(course, key=course):
                selected_courses_with_day.append((day, course))
                
    st.divider()
    
    if st.button("Submit Enrolment"):
        total_selected = len(selected_courses_with_day)
        
        # Check for day conflicts (more than 1 per day)
        day_counts = {}
        for day, course in selected_courses_with_day:
            day_counts[day] = day_counts.get(day, 0) + 1
            
        conflict_days = [day for day, count in day_counts.items() if count > 1]
        
        # Validation Logic
        if total_selected == 0:
            st.warning("Please select at least 1 course before submitting.")
            
        elif total_selected > 4:
            st.error(f"⚠️ You selected {total_selected} courses. You can only choose a maximum of 4.")
            
        elif conflict_days:
            # If they picked multiple on one day, stop them
            days_str = ", ".join(conflict_days)
            st.error(f"⚠️ Schedule Conflict! You selected multiple courses on: **{days_str}**. Please choose only 1 course per day.")
            
        else:
            # If all rules are followed, save the data
            with st.spinner("Saving your enrolment..."):
                final_courses = [item[1] for item in selected_courses_with_day]
                
                # Pad the list so it always has 4 items for the spreadsheet columns
                while len(final_courses) < 4:
                    final_courses.append("")
                
                # Prepare data
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
                
                # Send data to SheetDB
                response = requests.post(SHEETDB_URL, json=data)
                
                if response.status_code == 201:
                    st.success("✅ Enrolment successful! You can now close this window.")
                else:
                    st.error("Something went wrong. Please contact administration.")
