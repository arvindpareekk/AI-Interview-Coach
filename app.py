import streamlit as st
from openai import OpenAI
import pdfplumber

# ---------------------------
# OpenRouter Client
# ---------------------------

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

st.title("🤖 AI Interview Coach")
st.subheader("AI Powered Career Preparation Platform")

# ---------------------------
# Resume Upload
# ---------------------------

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

resume_text = ""

if resume_file:
    with pdfplumber.open(resume_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                resume_text += text

    st.success("Resume uploaded successfully")

# ---------------------------
# Interview Setup
# ---------------------------

interview_type = st.selectbox(
    "Select Interview Type",
    ["Select Interview Type", "Tech", "Non-Tech"]
)

role = st.text_input(
    "Enter Job Role",
    placeholder="Example: Java Developer"
)

# ---------------------------
# Session State
# ---------------------------

if "question_number" not in st.session_state:
    st.session_state.question_number = 0

if "question" not in st.session_state:
    st.session_state.question = None

if "feedback_list" not in st.session_state:
    st.session_state.feedback_list = []

# ---------------------------
# Start Interview
# ---------------------------

if st.button("Start Interview"):

    if interview_type == "Select Interview Type":
        st.warning("Please select interview type first")

    elif role.strip() == "":
        st.warning("Please enter job role")

    else:

        st.session_state.feedback_list = []

        prompt = f"""
        Candidate resume:
        {resume_text}

        Ask ONE interview question for the role {role}.
        If resume is available, use skills or projects from it.
        """

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        st.session_state.question = response.choices[0].message.content
        st.session_state.question_number = 1

# ---------------------------
# Interview Question
# ---------------------------

if st.session_state.question:

    st.write(f"### Question {st.session_state.question_number}/5")
    st.write(st.session_state.question)

    answer = st.text_area(
        "Your Answer",
        key=f"answer_{st.session_state.question_number}"
    )

    if st.button("Submit Answer"):

        if len(answer.strip()) < 10:
            st.error("Answer too short. Please provide a meaningful response.")
            st.stop()

        evaluation_prompt = f"""
        You are a strict technical interviewer.

        Question:
        {st.session_state.question}

        Candidate Answer:
        {answer}

        Evaluation Rules:
        - If the answer is irrelevant or extremely short, give score between 0 and 2.
        - If the answer partially answers the question, give score between 3 and 6.
        - If the answer is detailed and correct, give score between 7 and 10.

        Provide:

        Technical Score (0-10)
        Communication Score (0-10)
        Confidence Score (0-10)
        Short feedback explaining the scores.
        """

        eval_response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[{"role": "user", "content": evaluation_prompt}]
        )

        feedback = eval_response.choices[0].message.content

        st.write("### AI Evaluation")
        st.write(feedback)

        st.session_state.feedback_list.append(feedback)

        # ---------------------------
        # Next Question
        # ---------------------------

        if st.session_state.question_number < 5:

            prompt = f"""
            Ask another interview question for role {role}.
            Resume context:
            {resume_text}
            """

            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )

            st.session_state.question = response.choices[0].message.content
            st.session_state.question_number += 1

            st.rerun()

        # ---------------------------
        # Interview Finished
        # ---------------------------

        else:

            st.session_state.question = None

            st.success("Interview Completed 🎉")

            st.write("## Individual Question Feedback")

            for i, f in enumerate(st.session_state.feedback_list):
                st.write(f"### Question {i+1}")
                st.write(f)

            combined_feedback = "\n".join(st.session_state.feedback_list)

            report_prompt = f"""
            Based on the following interview feedback generate an overall report.

            Feedback:
            {combined_feedback}

            Provide:

            Overall Performance Score (out of 10)
            Candidate Strengths
            Weak Areas
            Communication Analysis
            Recommended Topics to Improve
            """

            report_response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=[{"role": "user", "content": report_prompt}]
            )

            final_report = report_response.choices[0].message.content

            st.write("## 📊 Overall Interview Report")
            st.write(final_report)