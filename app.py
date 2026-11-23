import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Course Enrolment Portal")

st.title("📚 Online Course Enrolment")
st.write("Please select a maximum of 4 courses.")

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

# Generate the 40 courses dynamically
COURSES = [f"MABC{str(i).zfill(4)} - Intro to course {str(i).zfill(3)}" for i in range(1, 41)]

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
    
    selected_courses = st.multiselect(
        "Choose your courses (Max 4):", 
        COURSES, 
        max_selections=4
    )
    
    if st.button("Submit Enrolment"):
        if len(selected_courses) == 0:
            st.warning("Please select at least 1 course before submitting.")
        else:
            with st.spinner("Saving your enrolment..."):
                while len(selected_courses) < 4:
                    selected_courses.append("")
                
                # Prepare data
                data = {
                    "data": [{
                        "Student Number": st.session_state.student_id,
                        "Course 1": selected_courses[0],
                        "Course 2": selected_courses[1],
                        "Course 3": selected_courses[2],
                        "Course 4": selected_courses[3],
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }]
                }
                
                # Send data to SheetDB
                response = requests.post(SHEETDB_URL, json=data)
                
                if response.status_code == 201:
                    st.success("✅ Enrolment successful! You can now close this window.")
                else:
                    st.error("Something went wrong. Please contact administration.")
