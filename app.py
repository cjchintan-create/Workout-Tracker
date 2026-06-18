import streamlit as st
import pandas as pd
import datetime
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# App Configuration
st.set_page_config(page_title="Aesthetic Tracker", page_icon="💪", layout="centered")

st.markdown("""
    <style>
    .main .block-container { max-width: 500px; padding-top: 2rem; }
    h1 { text-align: center; color: #2C3E50; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { width: 100%; background-color: #34495E; color: white; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #2C3E50; color: white; }
    .exercise-box { background-color: #F8F9FA; padding: 12px; border-radius: 8px; border-left: 6px solid #2C3E50; margin-top: 15px; margin-bottom: 10px; }
    .exercise-title { color: #2C3E50; font-size: 16px; font-weight: bold; margin-bottom: 2px; }
    .exercise-subtitle { color: #7F8C8D; font-size: 13px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("💪 Aesthetic Cloud Tracker")

EXCEL_FILE = "Aesthetic_Workout_Blueprint.xlsx"

# 🛠️ PASTE YOUR GOOGLE SHEET URL HERE
GSHEET_URL = "https://docs.google.com/spreadsheets/d/1iROHvJpaXnjYDDYQ3OAF1ruOMY4K16N0spz3cwnVRfA/edit?gid=0#gid=0"

# --- GOOGLE SHEETS AUTHENTICATION ---
# --- GOOGLE SHEETS AUTHENTICATION ---
def save_to_google_sheets(data_list):
    try:
        # Pull the service account keys securely from Streamlit's Vault
        import streamlit as st
        gc = gspread.service_account_from_dict(st.secrets["gspread"]["credentials"])
        sh = gc.open_by_url(GSHEET_URL)
        worksheet = sh.get_worksheet(0)
        
        # Append rows
        for row in data_list:
            worksheet.append_row([
                row["Date"], 
                row["Exercise Name"], 
                row["Target Area Focus"], 
                row["Set Number"], 
                row["Weight Logged (kg)"], 
                row["Reps Executed"]
            ])
        return True
    except Exception as e:
        st.error(f"Google Sheets Error: {e}")
        return False
    except Exception as e:
        st.error(f"Google Sheets Error: {e}")
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
                    <div class='exercise-subtitle'>Focus: {ex['target']} | Goal: {ex['sets']} Sets x {ex['reps']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            for set_index in range(1, ex['sets'] + 1):
                c1, c2, c3 = st.columns([1, 2, 2])
                with c1:
                    st.markdown(f"<p style='padding-top: 24px; text-align: center; font-weight: bold;'>Set {set_index}</p>", unsafe_allow_html=True)
                with c2:
                    w_input = st.number_input("Weight (kg)", min_value=0.0, step=2.5, key=f"w_{routine_input}_{ex['name']}_{set_index}")
                with c3:
                    r_input = st.number_input("Reps Completed", min_value=0, step=1, key=f"r_{routine_input}_{ex['name']}_{set_index}")
                
                if r_input > 0 or w_input > 0:
                    current_session_accumulator.append({
                        "Date": date_input.strftime("%Y-%m-%d"),
                        "Routine Day": routine_input,
                        "Exercise Name": ex['name'],
                        "Target Area Focus": ex['target'],
                        "Set Number": set_index,
                        "Weight Logged (kg)": w_input,
                        "Reps Executed": r_input
                    })
            st.markdown("<br>", unsafe_allow_html=True)
            
        st.markdown("---")
        if st.button("Save Training Session Logs to Cloud"):
            if current_session_accumulator:
                success = save_to_google_sheets(current_session_accumulator)
                if success:
                    st.success("Session saved directly to your Google Drive Sheet! 🚀")
                    st.balloons()
            else:
                st.warning("Please record data before saving.")

    with tab2:
        st.subheader("Google Sheet Cloud Overview")
        st.write(f"👉 [Click here to open your Google Sheet database]({GSHEET_URL})")
        st.info("Your full workout history is securely streaming live to your personal Google Drive profile.")
