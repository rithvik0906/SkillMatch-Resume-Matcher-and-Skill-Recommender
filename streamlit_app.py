import streamlit as st
import pandas as pd
import pdfplumber
import re
import plotly.graph_objects as go

# --- Skill List ---
skill_keywords = [
    'python', 'java', 'c++', 'sql', 'machine learning', 'deep learning', 
    'data analysis', 'data visualization', 'excel', 'tableau', 'power bi',
    'communication', 'teamwork', 'leadership', 'cloud', 'aws', 'azure',
    'react', 'javascript', 'node', 'html', 'css', 'nlp', 'statistics'
]

# --- Load Course Datasets ---
@st.cache_data
def load_courses():
    coursera = pd.read_csv("datasets/coursea_data.csv")
    udemy = pd.read_csv("datasets/udemy_courses.csv")
    return coursera, udemy

coursera, udemy = load_courses()

# --- Skill Extraction Function ---
def extract_skills(text):
    text = str(text).lower()
    found_skills = [skill for skill in skill_keywords if re.search(r'\b' + re.escape(skill) + r'\b', text)]
    return list(set(found_skills))

# --- PDF Text Extraction ---
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return " ".join([page.extract_text() or "" for page in pdf.pages])

# --- Course Suggestion Function ---
def suggest_courses(missing_skills):
    suggestions = []
    for skill in missing_skills:
        c_match = coursera[coursera['course_title'].str.contains(skill, case=False, na=False)]
        u_match = udemy[udemy['course_title'].str.contains(skill, case=False, na=False)]

        if not c_match.empty:
            suggestions.append({
                'Skill': skill,
                'Platform': 'Coursera',
                'Course': c_match.iloc[0]['course_title']
            })
        elif not u_match.empty:
            suggestions.append({
                'Skill': skill,
                'Platform': 'Udemy',
                'Course': u_match.iloc[0]['course_title'],
                'URL': u_match.iloc[0]['url']
            })
    return pd.DataFrame(suggestions)

# --- Streamlit App ---
st.set_page_config(page_title="SkillMatcher", page_icon="🧠", layout="wide")
st.title("🧠 SkillMatcher — Resume & Job Match Analyzer")

st.write("Upload your resume and paste a job description to see how well you match!")

uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("💼 Paste Job Description")

if uploaded_file and job_description:
    resume_text = extract_text_from_pdf(uploaded_file)
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    match_percent = (len(set(resume_skills) & set(job_skills)) / len(job_skills) * 100) if job_skills else 0
    missing_skills = list(set(job_skills) - set(resume_skills))

    st.subheader(f"🎯 Match Percentage: {match_percent:.2f}%")
    st.progress(int(match_percent))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Skills Found in Resume")
        st.write(", ".join(resume_skills) if resume_skills else "No skills detected.")

    with col2:
        st.markdown("### 💼 Skills Required by Job")
        st.write(", ".join(job_skills) if job_skills else "No skills detected.")

    # --- Skill Overlap Chart (Plotly Venn-style bar) ---
    st.markdown("### 📊 Skill Overlap Visualization")
    common = len(set(resume_skills) & set(job_skills))
    fig = go.Figure(data=[
        go.Bar(name='Resume', x=['Skills'], y=[len(resume_skills)]),
        go.Bar(name='Job Description', x=['Skills'], y=[len(job_skills)]),
        go.Bar(name='Matched', x=['Skills'], y=[common])
    ])
    fig.update_layout(barmode='group', xaxis_title="Skill Sets", yaxis_title="Count")
    st.plotly_chart(fig, use_container_width=True)

    # --- Missing Skills---
    if missing_skills:
        courses_df = suggest_courses(missing_skills)
    else:
        st.success("🎉 Great! You already have all the required skills.")
