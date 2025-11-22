import streamlit as st
import pandas as pd
import pdfplumber
import re
import plotly.graph_objects as go

# ------------------------------
# --- Skill List ---
# ------------------------------
skill_keywords = [
    'python', 'java', 'c++', 'sql', 'machine learning', 'deep learning',
    'data analysis', 'data visualization', 'excel', 'tableau', 'power bi',
    'communication', 'teamwork', 'leadership', 'cloud', 'aws', 'azure',
    'react', 'javascript', 'node', 'html', 'css', 'nlp', 'statistics'
]

# ------------------------------
# Load Course Datasets
# ------------------------------
@st.cache_data
def load_courses():
    coursera = pd.read_csv("datasets/coursera.csv")
    udemy = pd.read_csv("datasets/udemy.csv")
    return coursera, udemy

coursera, udemy = load_courses()

# ------------------------------
# Extract skills
# ------------------------------
def extract_skills(text):
    text = str(text).lower()
    found = [skill for skill in skill_keywords if re.search(r'\b' + re.escape(skill) + r'\b', text)]
    return list(set(found))

# ------------------------------
# PDF text extraction
# ------------------------------
def extract_text_from_pdf(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        return " ".join([page.extract_text() or "" for page in pdf.pages])

# ------------------------------
# Suggest courses
# ------------------------------
def suggest_courses(missing_skills):
    suggestions = []
    for skill in missing_skills:
        c_match = coursera[coursera['course_title'].str.contains(skill, case=False, na=False)]
        u_match = udemy[udemy['course_title'].str.contains(skill, case=False, na=False)]

        if not c_match.empty:
            suggestions.append({
                'Skill': skill,
                'Platform': 'Coursera',
                'Course': c_match.iloc[0]['course_title'],
                'URL': c_match.iloc[0]['url']
            })
        elif not u_match.empty:
            suggestions.append({
                'Skill': skill,
                'Platform': 'Udemy',
                'Course': u_match.iloc[0]['course_title'],
                'URL': u_match.iloc[0]['url']
            })
    return pd.DataFrame(suggestions)


# ----------------------------------------------------------
# -------------   UI DESIGN ENHANCEMENTS -------------------
# ----------------------------------------------------------

st.set_page_config(page_title="SkillMatcher", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
        * { font-family: 'Segoe UI', sans-serif; }

        .title {
            font-size: 40px !important;
            text-align: center;
            color: #1f4e79;
            padding-bottom: 5px;
        }

        h3 {
            color: #1f4e79 !important;
            margin-top: 25px !important;
        }

        .dataframe {
            font-size: 16px !important;
        }

        .stButton>button {
            background-color: #1f4e79;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 18px;
        }
        .stButton>button:hover {
            background-color: #163a5a;
            color: #f2f2f2;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title'>🧠 SkillMatcher — Resume & Job Match Analyzer</h1>", unsafe_allow_html=True)

st.write("Upload your resume and paste a job description to check your skill match.")


uploaded_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("💼 Paste Job Description", height=180)


# ----------------------------------------------------------
# --------- AUTO-RUN ANALYSIS WHEN BOTH ARE READY ----------
# ----------------------------------------------------------

if uploaded_file and job_description:

    # Extract text and skills
    resume_text = extract_text_from_pdf(uploaded_file)
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    # Match %
    match_percent = (
        len(set(resume_skills) & set(job_skills)) / len(job_skills) * 100
        if job_skills else 0
    )
    missing_skills = list(set(job_skills) - set(resume_skills))
    matched_skills = list(set(resume_skills) & set(job_skills))

    st.subheader(f"🎯 Match Percentage: {match_percent:.2f}%")
    st.progress(int(match_percent))

    # ---------------------------------------
    # Skill tables left + right
    # ---------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 Resume Skills")
        st.dataframe(pd.DataFrame({"Resume Skills": resume_skills}))

    with col2:
        st.markdown("### 💼 Job Required Skills")
        st.dataframe(pd.DataFrame({"Job Skills": job_skills}))

    # ---------------------------------------
    # BAR CHART
    # ---------------------------------------
    st.markdown("### 📊 Skill Overlap — Bar Graph")

    fig_bar = go.Figure(data=[
        go.Bar(name='Resume', x=['Skills'], y=[len(resume_skills)]),
        go.Bar(name='Job Description', x=['Skills'], y=[len(job_skills)]),
        go.Bar(name='Matched', x=['Skills'], y=[len(matched_skills)])
    ])

    fig_bar.update_layout(
        barmode='group',
        xaxis_title="Skill Sets",
        yaxis_title="Count"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------------------------------
    # PIE CHART
    # ---------------------------------------
    st.markdown("### 🥧 Match Breakdown — Pie Chart")

    fig_pie = go.Figure(data=[go.Pie(
        labels=['Matched Skills', 'Missing Skills'],
        values=[len(matched_skills), len(missing_skills)],
        hole=0.3
    )])

    fig_pie.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
