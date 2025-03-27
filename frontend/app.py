import streamlit as st
import requests

# Base API URL
BASE_URL = "http://127.0.0.1:8000/api"

# Initialize session state for token, candidate id, and job id
if "token" not in st.session_state:
    st.session_state.token = None
if "candidate_id" not in st.session_state:
    st.session_state.candidate_id = None

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Register", 
    "Login", 
    "Upload Resume", 
    "Post Job Description", 
    "View Profile", 
    "Match Candidate to Job"
])

def register():
    st.title("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    name = st.text_input("Name")
    password = st.text_input("Password", type="password")
    password2 = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        data = {
            "username": username,
            "email": email,
            "password": password,
            "password2": password2,
            "name": name
        }
        try:
            response = requests.post(f"{BASE_URL}/register/", json=data)
            if response.status_code in (200, 201):
                st.success("Registration successful!")
            else:
                st.error(f"Registration failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

def login():
    st.title("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        data = {
            "username": username,
            "password": password
        }
        try:
            response = requests.post(f"{BASE_URL}/login/", json=data)
            if response.status_code == 200:
                token = response.json().get("token")
                if token:
                    st.session_state.token = token
                    st.success("Logged in successfully!")
                else:
                    st.error("No token received. Check your credentials.")
            else:
                st.error(f"Login failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

def upload_resume():
    st.title("Upload Resume")
    if not st.session_state.token:
        st.warning("Please log in first.")
        return
    resume_file = st.file_uploader("Upload your resume", type=["pdf", "doc", "docx"])
    if st.button("Upload"):
        if resume_file is None:
            st.warning("Please upload a resume file.")
            return
        headers = {"Authorization": f"Token {st.session_state.token}"}
        files = {"resume": resume_file}
        try:
            response = requests.post(f"{BASE_URL}/candidates/upload_resume/", headers=headers, files=files)
            if response.status_code in (200, 201):
                data = response.json()
                st.session_state.candidate_id = data.get("id")
                st.success("Resume uploaded and parsed successfully!")
                st.write("Parsed Candidate Data:", data)
            else:
                st.error(f"Upload failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

def post_job_description():
    st.title("Post Job Description")
    if not st.session_state.token:
        st.warning("Please log in first.")
        return
    job_description = st.text_area("Enter Job Description")
    if st.button("Post Job"):
        data = {"job_description": job_description}
        headers = {"Authorization": f"Token {st.session_state.token}"}
        try:
            response = requests.post(f"{BASE_URL}/jobs/create_from_description/", json=data, headers=headers)
            if response.status_code in (200, 201):
                job_data = response.json()
                st.success("Job posted successfully!")
                st.write("Job Data:", job_data)
            else:
                st.error(f"Job post failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

def view_profile():
    st.title("View Profile")
    if not st.session_state.token:
        st.warning("Please log in first.")
        return
    headers = {"Authorization": f"Token {st.session_state.token}"}
    try:
        response = requests.get(f"{BASE_URL}/candidates/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                candidate_data = data["results"][0]
                st.write("Candidate Profile:", candidate_data)
                # Store candidate_id for matching
                st.session_state.candidate_id = candidate_data.get("id")
            else:
                st.info("No candidate profile found. Please upload your resume.")
        else:
            st.error(f"Failed to fetch profile: {response.text}")
    except Exception as e:
        st.error(f"Error: {e}")


def match_candidate_to_job():
    st.title("Match Candidate to Job")
    if not st.session_state.token:
        st.warning("Please log in first.")
        return

    # Fetch available jobs to populate the dropdown
    headers = {"Authorization": f"Token {st.session_state.token}"}
    try:
        response = requests.get(f"{BASE_URL}/jobs/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get("results", [])
        else:
            st.error(f"Failed to fetch jobs: {response.text}")
            jobs = []
    except Exception as e:
        st.error(f"Error fetching jobs: {e}")
        jobs = []

    # Create a mapping for job titles to job IDs
    job_options = {}
    for job in jobs:
        title = job.get("title", "No Title")
        job_id = job.get("id", "")
        if job_id:
            job_options[title] = job_id

    # Candidate ID (if available)
    candidate_id = st.text_input("Candidate ID", value=st.session_state.candidate_id if st.session_state.candidate_id else "")

    if not job_options:
        st.info("No jobs available to match. Please post a job description first or check the job listings.")
        return

    selected_job_title = st.selectbox("Select Job (by Title)", options=list(job_options.keys()))
    selected_job_id = job_options[selected_job_title]

    if st.button("Match"):
        data = {
            "candidate_id": candidate_id,
            "job_id": selected_job_id
        }
        try:
            response = requests.post(f"{BASE_URL}/matches/match_candidate_to_job/", json=data, headers=headers)
            if response.status_code == 200:
                match_data = response.json()
                st.success("Matching completed!")
                st.write("Match Score:", match_data.get("match_score"))
                st.write("Missing Skills:", match_data.get("missing_skills"))
                st.write("Summary:", match_data.get("summary"))
            else:
                st.error(f"Matching failed: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

if page == "Register":
    register()
elif page == "Login":
    login()
elif page == "Upload Resume":
    upload_resume()
elif page == "Post Job Description":
    post_job_description()
elif page == "View Profile":
    view_profile()
elif page == "Match Candidate to Job":
    match_candidate_to_job()