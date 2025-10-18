import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import uuid
# import ast

# File Handling

Data_Directory = "reports_data"
session_file = os.path.join(Data_Directory, "session_info.json")
csv_path = os.path.join(Data_Directory, "reports.csv")
os.makedirs(Data_Directory, exist_ok=True)


# Page configurations

st.set_page_config(page_title="User Side", layout="centered")

# Start session

def load_session():
    """Load session from json file, or return None if there is no session"""

    if os.path.exists(session_file):
        with open(session_file, "r", encoding="utf-8") as f:
            return json.load(f)
        
    else: 
        return None
    
# Save Session

def save_session(session_dict):
    """Save session dict to local JSON file."""
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_dict, f, indent=2)


# Clear session

def clear_session():
    """Clear session when sign out or stay away for 2 days"""

    if os.path.exists(session_file):
        os.remove(session_file)


# Save uploaded file

def save_uploaded_file(uploaded, dest_folder):
    """"Save upladed file if any or return None"""

    if uploaded is None:

        return None
    
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}_{uploaded.name}"
    path = os.path.join(dest_folder, unique_name)

    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())

    return unique_name


# Load current session - If any!

session = load_session()
st.markdown("##### Daily Mud Logging unit report - User Side")

# If there is no active session, show the start new session form.

if session is None:
    st.header("Start new session")
    st.info("Create a new session with Rig and unit numbers that will be remembered until you sign out")

    with st.form("start_session_form"):
        client = st.text_input("Client Name")
        rig_name = st.text_input("Rig Number")
        well_name = st.text_input("Well Name")
        unit_number = st.text_input("Unit Number")
        unit_supervisor = st.text_input("Unit Supervisor Name | Your Name")
        start_btn = st.form_submit_button("Start Session")

    if start_btn:

        if not rig_name or not well_name:
            st.error("Please Enter at least Rig and Well Names")

        else:
            session = {
                "rig_name": rig_name.strip().upper(),
                "well_name": well_name.strip().upper(),
                "client": client.strip().upper(),
                "unit_number": unit_number.strip(),
                "unit_supervisor": unit_supervisor.strip().capitalize(),
                "spud_date": datetime.now().strftime("%d-%m-%Y")
            }

            save_session(session)
            st.success("Session Started ✅")
            st.experimental_rerun()


else:
    st.success(f"##### Active Session: \
               \n**Rig** - {session.get('rig_name')} **|** **Well** - {session.get('well_name')}")
    
    st.write("**Client** : ", session.get("client") or "_")
    st.write("**Unit No.** : ", session.get("unit_number") or ("_"))
    st.write("**Currently Unit Supervisor** : ", session.get("unit_supervisor") or "_")
    st.write("**Spud Date**", session.get("spud_date"))


# Sign out button

if session is not None:

    col1, col2, col3 = st.columns([1,1,1])

    with col2:
        if st.button("Sign Out | End Session"):
            clear_session()
            st.success("Session Ended, you can now start new session!")
            st.experimental_rerun()

    
    st.markdown("---")

    # Today's report submission
    st.header("Submit today's daily report")

    with st.form("daily_report_form", clear_on_submit=True):
        
        today = datetime.now().strftime("%d-%m-%Y")
        st.write("**Today's Date |**", today)
        operation = st.selectbox("**Operation |**", ["Drilling", "Completion", "Rig Move"])
        depth = st.text_input("**Current Depth |**")
        remarks = st.text_area("**Current Operation Summary |**")
        daily_submit = st.form_submit_button("Submit")

    
    if daily_submit:
        record = {
            "Rig": session.get("rig_name"),
            "Client": session.get("client"),
            "Well Name": session.get("well_name"),
            "Unit Number": session.get("unit_number"),
            "Unit Supervisor": session.get("unit_supervisor"),
            "Spud Date": session.get("spud_date"),
            "Today Date": today,
            "Operation": operation,
            "Current Depth": depth,
            "Current Operation Summary": remarks
        }

        if not os.path.exists("csv_path"):
            df = pd.DataFrame([record])
            df.to_csv(csv_path, index= False, encoding= "utf-8")

        else:
            df = pd.read_csv(csv_path)
            df = pd.concat([df, pd.DataFrame([record])], ignore_index= True)
            df.to_csv(csv_path, index= False, encoding= "utf-8")

        st.success("Thank You!")
        st.write("### Today's Report Summary: ")

        record_df = pd.DataFrame(record.items(), columns=["Field", "Value"])
        record_df.index = record_df.index + 1
        st.table(record_df)
        # st.dataframe(record_df, use_container_width= True)