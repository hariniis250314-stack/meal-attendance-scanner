import streamlit as st
import cv2
from datetime import datetime
import pandas as pd
import os

# Set up the Streamlit page
st.set_page_config(page_title="Meal Attendance", page_icon="🍽️")
st.title("🍽️ Meal Attendance Scanner")

# CSV file for storing attendance
log_file = "meal_attendance_log.csv"

# Create CSV file if it doesn't exist
if not os.path.exists(log_file):
    df = pd.DataFrame(columns=["Timestamp"])
    df.to_csv(log_file, index=False)

# Load existing data
df = pd.read_csv(log_file)
attendance_count = len(df)

# Setup camera and UI
FRAME_WINDOW = st.image([])
run = st.checkbox("Start Camera")

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()
last_scan_time = None

while run:
    ret, frame = cap.read()
    if not ret:
        break

    data, bbox, _ = detector.detectAndDecode(frame)

    if data == "I came to eat":
        current_time = datetime.now()
        # Prevent duplicate scans within 3 seconds
        if last_scan_time is None or (current_time - last_scan_time).seconds > 3:
            new_entry = pd.DataFrame([[current_time.strftime("%Y-%m-%d %H:%M:%S")]], columns=["Timestamp"])
            new_entry.to_csv(log_file, mode="a", header=False, index=False)

            attendance_count += 1
            last_scan_time = current_time
            st.success(f"✅ Student Counted! Total Today: {attendance_count}")

    FRAME_WINDOW.image(frame)

cap.release()

# Show current total count
st.markdown("---")
st.metric("🍽️ Total Students Counted Today", attendance_count)
