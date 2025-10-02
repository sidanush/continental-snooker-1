import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

# ================== CONFIG ==================
st.set_page_config(page_title="Continental Snooker", page_icon="🎱", layout="wide")

# Prices per hour
PRICES = {
    "English Snooker Table 1": 200,
    "English Snooker Table 2": 200,
    "French Snooker Table": 250
}

# Excel file path
EXCEL_FILE = "snooker_bookings.xlsx"

# ================== CUSTOM CSS (THEME FIX) ==================
# This robust CSS block applies the background image and gold/black theme
# to the main Streamlit container (stApp) and internal elements.
st.markdown("""
    <style>
    /* 1. Background Image and Dark Overlay Fix: Targeting the main Streamlit container */
    /* This makes the background image visible and applies a dark filter */
    .stApp {
        background: url('https://images.unsplash.com/photo-1582120467325-5d9f96a7a5c3?auto=format&fit=crop&w=1920&q=80') no-repeat center center fixed;
        background-size: cover;
        position: relative;
    }
    .stApp::before {
        content: "";
        position: absolute; top:0; left:0; width:100%; height:100%;
        background: rgba(0,0,0,0.75); /* Dark overlay */
        z-index: 0;
    }
    
    /* 2. General Text and Header Color */
    .main, .stApp {
        color: #f5c518 !important; /* Gold text color */
        font-family: "Segoe UI", sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f5c518 !important; /* Make all headers gold */
    }

    /* 3. Input Fields (text_input, selectbox) Styling */
    /* Targets the input boxes to give them a black background and gold border/text */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stSelectbox>div>div {
        background-color: #1a1a1a !important; 
        color: #f5c518 !important; 
        border: 1px solid #f5c518 !important; 
        border-radius: 10px; 
        padding: 8px;
    }
    
    /* 4. Button Styling (Gold & Black) */
    .stButton>button {
        background: linear-gradient(90deg, #f5c518, #ffdf70);
        color:black !important; border-radius:12px; padding:10px 20px;
        font-weight:bold; border:none; box-shadow:0px 0px 10px rgba(245,197,24,0.6);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover { 
        background: linear-gradient(90deg, #ffdf70, #f5c518); 
        transform:scale(1.02); 
    }
    
    /* 5. Metrics/Stats Box Styling */
    [data-testid="stMetric"] {
        background-color: #1a1a1a;
        border: 1px solid #f5c518;
        border-radius: 10px;
        padding: 15px;
        box-shadow:0px 0px 10px rgba(245,197,24,0.3);
        margin-bottom: 10px;
    }
    
    /* Custom Box Class (for Booking Section and Quick Stats) */
    .custom-box {
        background-color:rgba(0,0,0,0.8); /* Slightly transparent black */
        padding:20px; 
        border-radius:15px;
        border: 2px solid #f5c518; /* Gold border */
        box-shadow: 0 0 15px rgba(245, 197, 24, 0.5); /* Gold glow */
        z-index: 10;
        position: relative; /* Ensure it stacks over the background */
    }
    
    /* Ensure all content sits above the Z-index 0 background overlay */
    .main [data-testid="stVerticalBlock"] {
        z-index: 10 !important;
    }
    
    </style>
""", unsafe_allow_html=True)
# ================== END CUSTOM CSS ==================


# ================== TITLE ==================
st.markdown(
    """
    <h1 style='text-align:center;'>🏆 Continental Snooker 🎱</h1>
    <h3 style='text-align:center;'>Welcome to Continental Snooker</h3>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ================== LAYOUT ==================
col1, col2 = st.columns(2)

# --- Booking Section ---
with col1:
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True) 
    st.subheader("📝 Booking Section")

    name = st.text_input("Customer Name")
    table = st.selectbox("Choose Table", list(PRICES.keys()))
    start_time = st.text_input("Enter Start Time (hh:mm AM/PM)", "02:00 PM")
    end_time = st.text_input("Enter End Time (hh:mm AM/PM)", "03:00 PM")

    if st.button("💾 Save Booking"):
        if not name.strip():
            st.error("❌ Customer Name cannot be empty.")
        else:
            try:
                # Convert times, making input case-insensitive for AM/PM
                start_dt = datetime.strptime(start_time.strip().upper(), "%I:%M %p")
                end_dt = datetime.strptime(end_time.strip().upper(), "%I:%M %p")

                # Handle cross-midnight bookings
                delta = end_dt - start_dt
                if delta.total_seconds() < 0:
                     delta += pd.Timedelta(days=1) 
                     
                if delta.total_seconds() <= 0:
                    st.error("❌ End time must be after start time.")
                else:
                    hours = delta.total_seconds() / 3600
                    price = round(hours * PRICES[table], 2)

                    # Load or create Excel
                    if os.path.exists(EXCEL_FILE):
                        df = pd.read_excel(EXCEL_FILE)
                    else:
                        df = pd.DataFrame(columns=["Name", "Table", "Time", "Price", "Date"])

                    # Append booking
                    new_row = {
                        "Name": name.strip(),
                        "Table": table,
                        "Time": f"{start_time} - {end_time}",
                        "Price": price,
                        "Date": datetime.today().strftime("%Y-%m-%d")
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_excel(EXCEL_FILE, index=False)

                    st.success(f"✅ Booking saved! Total Price: ₹{price:,.2f}")
                    st.balloons() 

            except ValueError: 
                st.error("⚠️ Invalid time format. Please use hh:mm AM/PM (e.g., 02:30 PM).")
            except Exception as e:
                 st.error(f"⚠️ An unexpected error occurred: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Quick Stats Section ---
with col2:
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True) 
    st.subheader("📊 Quick Stats")

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0) 
        
        total_bookings = len(df)
        total_revenue = df["Price"].sum()
        today_revenue = df[df["Date"] == datetime.today().strftime("%Y-%m-%d")]["Price"].sum()

        st.metric("Total Bookings", total_bookings)
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        st.metric("Today's Revenue", f"₹{today_revenue:,.2f}")

        # Download button preparation
        towrite = BytesIO()
        df.to_excel(towrite, index=False, engine="openpyxl")
        towrite.seek(0)
        
        st.download_button(
            label="📥 Download Bookings Excel",
            data=towrite,
            file_name="snooker_bookings.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("No bookings yet!")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---") 

# --- Display existing bookings ---
st.subheader("All Bookings")
if os.path.exists(EXCEL_FILE):
    df_all = pd.read_excel(EXCEL_FILE)
    st.dataframe(df_all.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
else:
    st.info("No bookings saved yet.")

# ================== NGROK SECTION (For deployment/sharing) ==================

# If you want to share your app over the internet after running it locally,
# place this code block in a new, separate file (e.g., run_ngrok.py) 
# and execute it after the Streamlit app is running. 

# If you need to run it directly, uncomment the block below.

# from pyngrok import ngrok
# NGROK_AUTH_TOKEN = "33PmQ6vzuFOQ35AmEFnelDviXf0_3A2qa8VFy6yCLthHam21Q"
# NGROK_PORT = 8501 

# if 'ngrok_started' not in st.session_state:
#     try:
#         ngrok.set_auth_token(NGROK_AUTH_TOKEN)
#         public_url = ngrok.connect(NGROK_PORT)
#         st.session_state['public_url'] = public_url.public_url
#         st.session_state['ngrok_started'] = True
#     except Exception as e:
#         st.error(f"Failed to start ngrok: {e}")

# if 'public_url' in st.session_state:
#     st.markdown(f"**Public URL:** [{st.session_state['public_url']}]({st.session_state['public_url']})")import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO

# ================== CONFIG ==================
st.set_page_config(page_title="Continental Snooker", page_icon="🎱", layout="wide")

# Prices per hour
PRICES = {
    "English Snooker Table 1": 200,
    "English Snooker Table 2": 200,
    "French Snooker Table": 250
}

# Excel file path
EXCEL_FILE = "snooker_bookings.xlsx"

# ================== CUSTOM CSS (THEME FIX) ==================
# This robust CSS block applies the background image and gold/black theme
# to the main Streamlit container (stApp) and internal elements.
st.markdown("""
    <style>
    /* 1. Background Image and Dark Overlay Fix: Targeting the main Streamlit container */
    /* This makes the background image visible and applies a dark filter */
    .stApp {
        background: url('https://images.unsplash.com/photo-1582120467325-5d9f96a7a5c3?auto=format&fit=crop&w=1920&q=80') no-repeat center center fixed;
        background-size: cover;
        position: relative;
    }
    .stApp::before {
        content: "";
        position: absolute; top:0; left:0; width:100%; height:100%;
        background: rgba(0,0,0,0.75); /* Dark overlay */
        z-index: 0;
    }
    
    /* 2. General Text and Header Color */
    .main, .stApp {
        color: #f5c518 !important; /* Gold text color */
        font-family: "Segoe UI", sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f5c518 !important; /* Make all headers gold */
    }

    /* 3. Input Fields (text_input, selectbox) Styling */
    /* Targets the input boxes to give them a black background and gold border/text */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stSelectbox>div>div {
        background-color: #1a1a1a !important; 
        color: #f5c518 !important; 
        border: 1px solid #f5c518 !important; 
        border-radius: 10px; 
        padding: 8px;
    }
    
    /* 4. Button Styling (Gold & Black) */
    .stButton>button {
        background: linear-gradient(90deg, #f5c518, #ffdf70);
        color:black !important; border-radius:12px; padding:10px 20px;
        font-weight:bold; border:none; box-shadow:0px 0px 10px rgba(245,197,24,0.6);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover { 
        background: linear-gradient(90deg, #ffdf70, #f5c518); 
        transform:scale(1.02); 
    }
    
    /* 5. Metrics/Stats Box Styling */
    [data-testid="stMetric"] {
        background-color: #1a1a1a;
        border: 1px solid #f5c518;
        border-radius: 10px;
        padding: 15px;
        box-shadow:0px 0px 10px rgba(245,197,24,0.3);
        margin-bottom: 10px;
    }
    
    /* Custom Box Class (for Booking Section and Quick Stats) */
    .custom-box {
        background-color:rgba(0,0,0,0.8); /* Slightly transparent black */
        padding:20px; 
        border-radius:15px;
        border: 2px solid #f5c518; /* Gold border */
        box-shadow: 0 0 15px rgba(245, 197, 24, 0.5); /* Gold glow */
        z-index: 10;
        position: relative; /* Ensure it stacks over the background */
    }
    
    /* Ensure all content sits above the Z-index 0 background overlay */
    .main [data-testid="stVerticalBlock"] {
        z-index: 10 !important;
    }
    
    </style>
""", unsafe_allow_html=True)
# ================== END CUSTOM CSS ==================


# ================== TITLE ==================
st.markdown(
    """
    <h1 style='text-align:center;'>🏆 Continental Snooker 🎱</h1>
    <h3 style='text-align:center;'>Welcome to Continental Snooker</h3>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ================== LAYOUT ==================
col1, col2 = st.columns(2)

# --- Booking Section ---
with col1:
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True) 
    st.subheader("📝 Booking Section")

    name = st.text_input("Customer Name")
    table = st.selectbox("Choose Table", list(PRICES.keys()))
    start_time = st.text_input("Enter Start Time (hh:mm AM/PM)", "02:00 PM")
    end_time = st.text_input("Enter End Time (hh:mm AM/PM)", "03:00 PM")

    if st.button("💾 Save Booking"):
        if not name.strip():
            st.error("❌ Customer Name cannot be empty.")
        else:
            try:
                # Convert times, making input case-insensitive for AM/PM
                start_dt = datetime.strptime(start_time.strip().upper(), "%I:%M %p")
                end_dt = datetime.strptime(end_time.strip().upper(), "%I:%M %p")

                # Handle cross-midnight bookings
                delta = end_dt - start_dt
                if delta.total_seconds() < 0:
                     delta += pd.Timedelta(days=1) 
                     
                if delta.total_seconds() <= 0:
                    st.error("❌ End time must be after start time.")
                else:
                    hours = delta.total_seconds() / 3600
                    price = round(hours * PRICES[table], 2)

                    # Load or create Excel
                    if os.path.exists(EXCEL_FILE):
                        df = pd.read_excel(EXCEL_FILE)
                    else:
                        df = pd.DataFrame(columns=["Name", "Table", "Time", "Price", "Date"])

                    # Append booking
                    new_row = {
                        "Name": name.strip(),
                        "Table": table,
                        "Time": f"{start_time} - {end_time}",
                        "Price": price,
                        "Date": datetime.today().strftime("%Y-%m-%d")
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_excel(EXCEL_FILE, index=False)

                    st.success(f"✅ Booking saved! Total Price: ₹{price:,.2f}")
                    st.balloons() 

            except ValueError: 
                st.error("⚠️ Invalid time format. Please use hh:mm AM/PM (e.g., 02:30 PM).")
            except Exception as e:
                 st.error(f"⚠️ An unexpected error occurred: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# --- Quick Stats Section ---
with col2:
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True) 
    st.subheader("📊 Quick Stats")

    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0) 
        
        total_bookings = len(df)
        total_revenue = df["Price"].sum()
        today_revenue = df[df["Date"] == datetime.today().strftime("%Y-%m-%d")]["Price"].sum()

        st.metric("Total Bookings", total_bookings)
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        st.metric("Today's Revenue", f"₹{today_revenue:,.2f}")

        # Download button preparation
        towrite = BytesIO()
        df.to_excel(towrite, index=False, engine="openpyxl")
        towrite.seek(0)
        
        st.download_button(
            label="📥 Download Bookings Excel",
            data=towrite,
            file_name="snooker_bookings.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("No bookings yet!")

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---") 

# --- Display existing bookings ---
st.subheader("All Bookings")
if os.path.exists(EXCEL_FILE):
    df_all = pd.read_excel(EXCEL_FILE)
    st.dataframe(df_all.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
else:
    st.info("No bookings saved yet.")
