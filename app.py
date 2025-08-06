import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
from datetime import datetime
import pandas as pd
import os

# CSV file setup
log_file = "meal_attendance_log.csv"

if not os.path.exists(log_file):
    df = pd.DataFrame(columns=["Timestamp"])
    df.to_csv(log_file, index=False)

# Read existing log
df = pd.read_csv(log_file)
attendance_count = len(df)

st.set_page_config(page_title="Meal QR Counter", page_icon="🍽️")
st.title("🍽️ Meal Attendance QR Scanner (Streamlit Cloud)")

st.metric("🍽️ Total Students Counted", attendance_count)


# QR Scanner class
class QRScanner(VideoTransformerBase):
    def __init__(self):
        self.last_scanned = None
        self.last_scan_time = None

    def transform(self, frame):
        image = frame.to_ndarray(format="bgr24")
        qr_detector = cv2.QRCodeDetector()
        data, bbox, _ = qr_detector.detectAndDecode(image)

        if data == "I came to eat":
            now = datetime.now()
            if (
                self.last_scan_time is None
                or (now - self.last_scan_time).seconds > 3
            ):
                new_row = pd.DataFrame(
                    [[now.strftime("%Y-%m-%d %H:%M:%S")]], columns=["Timestamp"]
                )
                new_row.to_csv(log_file, mode="a", header=False, index=False)
                self.last_scan_time = now
                st.experimental_rerun()  # update counter

        return image


webrtc_streamer(
    key="qr",
    video_processor_factory=QRScanner,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

