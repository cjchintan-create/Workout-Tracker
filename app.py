import streamlit as st
import pandas as pd
import datetime
import os

# App Configuration
st.set_page_config(page_title="Aesthetic Tracker", page_icon="💪", layout="centered")

st.markdown("""
    <style>
    .main .block-container {
        max-width: 500px;
        padding-top: 2rem;
    }
    h1 {
        text-align: center;
        color: #2C3E50;
        font-family: 'Segoe UI', sans-serif;
    }
    .stButton>button {
        width: 100%;
        background-color: #34495E;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2C3E50;
        color: white;
    }
    .exercise-box {
        background-color: #F8F9FA;
        padding: 12px;
        border-radius: 8px;
        border-left: 6px solid #2C3E50;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .exercise-title {
        color: #2C3E50;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .exercise-subtitle {
        color: #7F8C8D;
        font-size: 13px;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💪 Aesthetic Cloud Tracker")

EXCEL_FILE = "Aesthetic_Workout_Blueprint.xlsx"

# --- GOOGLE SHEETS WEB APP AUTHENTICATION ---
def save_to_google_sheets(data_list):
    try:
        import requests
        import json
        
        # Live Google Apps Script Deployment URL
        WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxBgX83ovW2zWoq_-SyQEEGJQvJ5ESQzheCMPFwbCbKmGT5Ujyo0fpM2BMRmJfsAvbm/exec"
        
        response = requests.post(WEB_APP_URL, json=data_list)
        if response.status_code == 200 and response.json().get("status") == "success":
            return True
        else:
            st.error(f"Sheet Web App Error: {response.text}")
            return False
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return False

# --- LOAD EXCEL TEMPLATE ---
@st.cache_data
def load_workout_blueprint(file_path):
    try:
        df = pd.read_excel(file_path, skiprows=5)
        df.columns = [str(c).strip() for c in df.columns]
        
        workout_map = {}
        for day, group in df.groupby("Routine Day"):
            workout_map[day] = []
            for _, row in group.iterrows():
                workout_map[day].append({
                    "name": str(row["Exercise Name"]).strip(),
                    "target": str(row["Target Muscle Head"]).strip(),
                    "sets": int(row["Sets Plan"]),
                    "reps": str(row["Reps Plan"]).strip(),
                    "rest": str(row["Rest Target"]).strip()
                })
        return workout_map
    except Exception as e:
        st.error(f"Error reading Excel template: {e}")
        return None

WORKOUT_DICT = load_workout_blueprint(EXCEL_FILE)

if WORKOUT_DICT is not None:
    tab1, tab2 = st.tabs(["📝 Record Workout", "📊 Live Cloud Logs"])
    
    with tab1:
        date_input = st.date_input("Training Date", datetime.date.today())
        routine_input = st.selectbox("Choose Routine Day", list(WORKOUT_DICT.keys()))
        
        st.markdown("---")
        
        current_session_accumulator = []
        active_exercises_list = WORKOUT_DICT[routine_input]
        
        for ex in active_exercises_list:
            st.markdown(f"""
                <div class='exercise-box'>
                    <div class='exercise-title'>{ex['name']}</div>
                    <div class='exercise-subtitle'>{ex['target']} | Plan: {ex['sets']} Sets x {ex['reps']} (Rest: {ex['rest']})</div>
                </div>
            """, unsafe_allow_html=True)
            
            for set_num in range(1, ex['sets'] + 1):
                col1, col2 = st.columns(2)
                with col1:
                    weight = st.number_input(f"Weight (kg) - Set {set_num}", min_value=0.0, max_value=500.0, step=2.5, key=f"{ex['name']}_w_{set_num}")
                with col2:
                    reps = st.number_input(f"Reps Completed - Set {set_num}", min_value=0, max_value=100, step=1, key=f"{ex['name']}_r_{set_num}")
                
                current_session_accumulator.append({
                    "Date": str(date_input),
                    "Exercise Name": ex['name'],
                    "Target Area Focus": ex['target'],
                    "Set Number": set_num,
                    "Weight Logged (kg)": weight,
                    "Reps Executed": reps
                })
        
        if st.button("Save Training Session Logs to Cloud"):
            if save_to_google_sheets(current_session_accumulator):
                st.success("Workout successfully synced to Google Sheets!")
                st.balloons()
