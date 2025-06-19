import streamlit as st
import re
import os
from dotenv import load_dotenv
from llm_utils import generate_tech_questions, parse_tech_stack
import sqlite3
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI-Powered Interview Assistant | TalentScout",
    page_icon="🤖",
    layout="wide"
)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        name TEXT,
        email TEXT,
        phone TEXT,
        experience REAL,
        role TEXT,
        location TEXT,
        tech_stack TEXT,
        questions TEXT,
        answers TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Constants
STEP_LABELS = {
    "greeting": "👋 Welcome",
    "form": "📝 Candidate Information",
    "tech_stack": "🛠️ Technical Skills",
    "questions": "❓ Technical Assessment",
    "review": "🔍 Review Answers",
    "end": "🏁 Complete"
}

# Initialize session state
def init_session_state():
    if "step" not in st.session_state:
        st.session_state.step = "greeting"
    if "candidate_info" not in st.session_state:
        st.session_state.candidate_info = {}
    if "tech_stack" not in st.session_state:
        st.session_state.tech_stack = []
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

init_session_state()

# UI Components
def show_progress(current, total):
    progress = current / total
    st.progress(progress)
    st.caption(f"Progress: {current} of {total} ({int(progress*100)}%)")

def validate_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email.strip())

def validate_phone(phone):
    return re.match(r"^\+?[\d\s-]{10,15}$", phone.strip())

def generate_summary_text():
    summary = []
    summary.append("TALENTSCOUT APPLICATION SUMMARY")
    summary.append(f"Timestamp: {datetime.now().isoformat()}")
    summary.append("\n=== CANDIDATE INFORMATION ===")
    for key, value in st.session_state.candidate_info.items():
        summary.append(f"{key.title()}: {value}")
    
    summary.append("\n=== TECHNICAL SKILLS ===")
    summary.append(", ".join([tech for tech in st.session_state.tech_stack if len(tech) > 1]))
    
    summary.append("\n=== QUESTIONS & ANSWERS ===")
    for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
        summary.append(f"\nQ{i+1}: {q}")
        summary.append(f"A: {a}")
    
    return "\n".join(summary)

# Save to database
def save_to_db():
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    c.execute('''INSERT INTO candidates (
        timestamp, name, email, phone, experience, role, location, tech_stack, questions, answers
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        datetime.now().isoformat(),
        st.session_state.candidate_info.get("name", ""),
        st.session_state.candidate_info.get("email", ""),
        st.session_state.candidate_info.get("phone", ""),
        st.session_state.candidate_info.get("experience", 0),
        st.session_state.candidate_info.get("role", ""),
        st.session_state.candidate_info.get("location", ""),
        ",".join(st.session_state.tech_stack),
        ";".join(st.session_state.questions),
        ";".join(st.session_state.answers)
    ))
    conn.commit()
    conn.close()

# Step: Greeting (Chat-based)
if st.session_state.step == "greeting":
    st.title("Welcome to TalentScout!")
    st.markdown("Hi! I'm TalentScout's Hiring Assistant. Ready to showcase your skills? Let's start with your name!")

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    user_input = st.chat_input("Your response...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        end_keywords = ["exit", "quit", "done", "stop"]
        if any(keyword in user_input.lower() for keyword in end_keywords):
            st.session_state.chat_history.append({"role": "assistant", "content": "Thank you for your time! If you change your mind, feel free to restart."})
            st.session_state.step = "end"
        else:
            st.session_state.candidate_info["name"] = user_input.strip()
            st.session_state.chat_history.append({"role": "assistant", "content": f"Nice to meet you, {user_input.strip()}! Let's continue with your information."})
            st.session_state.step = "form"
        st.rerun()

# Step: Candidate Information
elif st.session_state.step == "form":
    st.title("Candidate Information")
    st.write(f"Hello {st.session_state.candidate_info['name']}! Let's collect some basic information.")
    
    with st.form("candidate_form"):
        cols = st.columns(3)
        with cols[0]:
            email = st.text_input("Email*", placeholder="john@example.com")
        with cols[1]:
            phone = st.text_input("Phone*", placeholder="+1 1234567890")
            experience = st.number_input("Experience (Years)*", min_value=0, max_value=50)
        with cols[2]:
            role = st.text_input("Position*", placeholder="Software Engineer")
            location = st.text_input("Location*", placeholder="City, Country")
        
        submitted = st.form_submit_button("Continue →")

    if submitted:
        errors = []
        if not validate_email(email):
            errors.append("Please enter a valid email address")
        if not validate_phone(phone):
            errors.append("Please enter a valid phone number (10-15 digits)")
        if not role.strip():
            errors.append("Please specify desired position(s)")
        if not location.strip():
            errors.append("Please enter your current location")
        if errors:
            for error in errors:
                st.error(error)
        else:
            st.session_state.candidate_info.update({
                "email": email.strip(),
                "phone": phone.strip(),
                "experience": experience,
                "role": role.strip(),
                "location": location.strip()
            })
            st.session_state.step = "tech_stack"
            st.rerun()

# Step: Technical Skills
elif st.session_state.step == "tech_stack":
    st.title("Technical Skills Assessment")
    st.success(f"Hello {st.session_state.candidate_info['name']}! Let's discuss your technical skills.")
    
    with st.form("tech_stack_form"):
        st.write("Please list the technologies, frameworks, and tools you're proficient in:")
        tech_input = st.text_area(
            "Tech Stack*",
            placeholder="Python, JavaScript, React, PostgreSQL, Docker...",
            height=150
        )
        
        submitted = st.form_submit_button("Generate Questions →")

    if submitted:
        if not tech_input.strip():
            st.error("Please enter at least one technology")
        else:
            tech_list = parse_tech_stack(tech_input)
            if len(tech_list) == 0:
                st.error("Could not identify any technologies. Please use standard names.")
            else:
                st.session_state.tech_stack = tech_list
                st.session_state.step = "questions"
                st.session_state.questions = []
                st.session_state.answers = []
                st.session_state.current_question_index = 0
                st.rerun()

# Step: Technical Questions
elif st.session_state.step == "questions":
    st.title("Technical Assessment")
    
    if not st.session_state.questions:
        with st.spinner("Generating customized questions based on your skills..."):
            try:
                questions = generate_tech_questions(
                    st.session_state.tech_stack,
                    st.session_state.candidate_info["experience"]
                )
                st.session_state.questions = [q for q in questions if q and ":" in q]
                if not st.session_state.questions:
                    raise ValueError("No valid questions generated")
            except Exception as e:
                st.error(f"Failed to generate questions: {str(e)}. Please try again with different technologies.")
                st.session_state.step = "tech_stack"
                st.rerun()

    current_idx = st.session_state.current_question_index
    total_questions = len(st.session_state.questions)

    if current_idx < total_questions:
        show_progress(current_idx + 1, total_questions)
        
        current_question = st.session_state.questions[current_idx]
        tech, question = current_question.split(':', 1)
        st.subheader(f"Question {current_idx + 1}/{total_questions} ({tech.strip()})")
        st.markdown(f"**{question.strip()}**")
        
        answer_key = f"answer_{current_idx}"
        answer = st.text_area(
            "Your answer:", 
            key=answer_key, 
            height=200,
            value=st.session_state.answers[current_idx] if current_idx < len(st.session_state.answers) else ""
        )
        
        cols = st.columns([1, 1, 2])
        with cols[0]:
            if st.button("← Previous", disabled=current_idx == 0, key=f"prev_{current_idx}"):
                st.session_state.current_question_index -= 1
                st.rerun()
        with cols[1]:
            next_disabled = not answer.strip()
            if st.button("Next →", disabled=next_disabled, key=f"next_{current_idx}"):
                while len(st.session_state.answers) <= current_idx:
                    st.session_state.answers.append("")
                st.session_state.answers[current_idx] = answer.strip()
                st.session_state.current_question_index += 1
                st.rerun()
        
        with st.expander("Finish early"):
            if st.button("Complete Assessment", key=f"complete_{current_idx}"):
                st.session_state.step = "review"
                st.rerun()
    else:
        st.session_state.step = "review"
        st.rerun()

# Step: Review Answers
elif st.session_state.step == "review":
    st.title("Review Your Answers")
    st.write("Please review your responses before submission.")
    
    for i, (question, answer) in enumerate(zip(st.session_state.questions, st.session_state.answers)):
        with st.expander(f"Question {i+1}: {question}"):
            st.write(answer)
            if st.button("Edit", key=f"edit_{i}"):
                st.session_state.current_question_index = i
                st.session_state.step = "questions"
                st.rerun()
    
    if st.button("Submit Assessment"):
        save_to_db()
        st.session_state.step = "end"
        st.rerun()
    
    if st.button("← Back to Questions"):
        st.session_state.current_question_index = len(st.session_state.questions) - 1
        st.session_state.step = "questions"
        st.rerun()

# Step: Completion
elif st.session_state.step == "end":
    st.title("🎉 Assessment Complete")
    st.markdown("""
<div style='background:#f0f2f6; padding:20px; border-radius:10px'>
    <h3 style='color:#2c3e50'>TalentScout Assessment Complete</h3>
    <p>Thank you for your time. Our team will review your responses shortly.</p>
</div>
""", unsafe_allow_html=True)
    
    st.success("""
    **Thank you for completing the assessment!**  
    We'll review your responses and contact you within 3-5 business days.
    """)
    
    with st.container(border=True):
        st.markdown(f"""
        **Candidate:** {st.session_state.candidate_info.get("name", "N/A")}  
        **Role:** {st.session_state.candidate_info.get("role", "N/A")}  
        **Experience:** {st.session_state.candidate_info.get("experience", 0)} years  
        **Location:** {st.session_state.candidate_info.get("location", "N/A")}
        """)
        tech_stack = [tech for tech in st.session_state.tech_stack if len(tech) > 1]
        if tech_stack:
            st.markdown("**Technical Skills:** " + ", ".join(tech_stack))
        else:
            st.warning("No technical skills specified")
        st.markdown(f"**Questions Completed:** {len(st.session_state.answers)}/{len(st.session_state.questions)}")

    st.download_button(
        label="📄 Download Full Summary",
        data=generate_summary_text(),
        file_name="talent_scout_summary.txt",
        mime="text/plain",
        use_container_width=True
    )
    
    if st.button("🔄 Start New Assessment", use_container_width=True, key="restart_button"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_session_state()
        st.rerun()
