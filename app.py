
import streamlit as st
import serial
import time
from datetime import datetime

st.set_page_config(
    page_title="Smart Home Security",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Smart Home Security Dashboard")
st.caption("Arduino Uno | PIR Motion Sensor | USB Monitoring")

# Arduino settings
PORT = "COM6"
BAUD_RATE = 9600

# Dashboard placeholders
status_area = st.empty()
metrics_area = st.empty()
activity_area = st.empty()

# Event data
events = []
motion_count = 0
motion_status = "CLEAR"
last_event = "Waiting for sensor..."

try:
    arduino = serial.Serial(
        PORT,
        BAUD_RATE,
        timeout=0.2
    )

    # Arduino resets when serial connection opens
    time.sleep(2)
    arduino.reset_input_buffer()

    st.success(f"Connected to Arduino on {PORT}")

    while True:

        if arduino.in_waiting:
            data = arduino.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            if data == "MOTION":
                motion_status = "MOTION"
                motion_count += 1

                last_event = datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

                events.insert(0, {
                    "Time": last_event,
                    "Event": "Motion Detected",
                    "Buzzer": "ON"
                })

            elif data == "CLEAR":
                motion_status = "CLEAR"

                last_event = datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

                events.insert(0, {
                    "Time": last_event,
                    "Event": "Area Clear",
                    "Buzzer": "OFF"
                })

            events = events[:20]

        # Live status
        with status_area.container():
            if motion_status == "MOTION":
                st.error("🚨 INTRUDER ALERT - MOTION DETECTED")
            else:
                st.success("✅ AREA CLEAR - NO MOTION")

        with metrics_area.container():
            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Motion Status",
                motion_status
            )

            c2.metric(
                "Buzzer Status",
                "ON" if motion_status == "MOTION" else "OFF"
            )

            c3.metric(
                "Total Motion Events",
                motion_count
            )

            st.caption(f"Last event: {last_event}")

        with activity_area.container():
            st.subheader("📋 Recent Activity")

            if events:
                st.dataframe(
                    events,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Waiting for motion events...")

        time.sleep(0.2)

except serial.SerialException as e:
    st.error(f"Arduino connection error: {e}")
    st.info("Check USB cable, COM port and close Arduino Serial Monitor.")

except KeyboardInterrupt:
    st.warning("Monitoring stopped.")
