import os
os.environ["STREAMLIT_DISABLE_ARROW"] = "1"

import streamlit as st
import pandas as pd
import json
import random
import google.generativeai as genai

# 🔑 Add your Gemini API key here
genai.configure(api_key="AIzaSyDg1cklXexWy4R8M4t_UOrlkIODa5mIEao")

model = genai.GenerativeModel("gemini-pro")

# Page config
st.set_page_config(page_title="AI Talent Agent", layout="wide")

# Load candidates
with open("candidates.json") as f:
    candidates = json.load(f)

# -------- FUNCTIONS --------

# AI Skill Extraction
def extract_skills(jd_text):
    try:
        prompt = f"""
        Extract key technical skills from this job description.
        Return only comma-separated skills.

        JD: {jd_text}
        """
        response = model.generate_content(prompt)
        skills = response.text.split(",")
        return [s.strip().lower() for s in skills if s.strip() != ""]
    except:
        return ["python", "sql"]

# Matching logic
def calculate_match(candidate, jd_skills):
    matched = list(set([s.lower() for s in candidate["skills"]]) & set(jd_skills))
    score = len(matched) * 20 + candidate["experience"] * 5
    return min(score, 100), matched

# AI Interest Simulation
def simulate_interest(candidate, jd_text):
    try:
        prompt = f"""
        Candidate Name: {candidate['name']}
        Skills: {candidate['skills']}
        Experience: {candidate['experience']} years

        Job Description: {jd_text}

        Give:
        Score: (0-100)
        Reason: why candidate is interested
        """

        response = model.generate_content(prompt)
        text = response.text

        score = 70
        reason = "Good fit"

        for line in text.split("\n"):
            if "Score" in line:
                try:
                    score = int(line.split(":")[1].strip())
                except:
                    pass
            if "Reason" in line:
                reason = line.split(":", 1)[1].strip()

        return score, reason
    except:
        return random.randint(60, 90), "Simulated interest"

# -------- UI --------

st.title("🤖 AI Talent Scouting & Engagement Agent")
st.text("AI-powered candidate matching using Gemini")

jd_input = st.text_area("📄 Paste Job Description", height=150)

if st.button("🔍 Run AI Agent"):

    if jd_input.strip() == "":
        st.text("Please enter a Job Description")
    else:
        st.text("Using Gemini AI...")

        # Extract skills
        jd_skills = extract_skills(jd_input)

        st.text("Extracted Skills:")
        st.text(", ".join(jd_skills))

        results = []

        for c in candidates:
            match_score, matched_skills = calculate_match(c, jd_skills)
            interest_score, reason = simulate_interest(c, jd_input)

            results.append({
                "Name": c["name"],
                "Match Score": match_score,
                "Interest Score": interest_score,
                "Matched Skills": ", ".join(matched_skills),
                "Interest Reason": reason,
                "Final Score": match_score * 0.6 + interest_score * 0.4
            })

        df = pd.DataFrame(results)
        df = df.sort_values(by="Final Score", ascending=False)

        st.text("Ranking is based on skill match + experience + AI interest score")

        st.text("Ranked Candidates:")

        for i, row in df.iterrows():
            st.text(
                f"{i+1}. {row['Name']} | Match: {row['Match Score']} | "
                f"Interest: {row['Interest Score']} | Final: {round(row['Final Score'],2)}"
            )
            st.text(f"   Skills: {row['Matched Skills']}")
            st.text(f"   Reason: {row['Interest Reason']}")
            st.text("")

        st.text(f"🎯 Top Candidate: {df.iloc[0]['Name']}")