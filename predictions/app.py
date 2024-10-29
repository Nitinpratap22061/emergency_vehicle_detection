import streamlit as st
import cv2
import numpy as np
from datetime import timedelta
from helper import YOLO_Pred

# Initialize YOLO_Pred with your model and YAML configuration
yolo = YOLO_Pred('predictions/hell/weights/best.onnx', 'predictions/data.yaml')

# Streamlit app title and description
st.set_page_config(page_title="YOLO Object Detection", layout="wide")
st.title("🔍 YOLO Object Detection")
st.write("Upload a video to detect objects in real-time.")

# File uploader for videos
uploaded_file = st.file_uploader("Choose a video...", type=["mp4"])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded video
    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("Video uploaded! Processing...")

    # Video capture
    video_file = cv2.VideoCapture(temp_video_path)

    # Create a placeholder for video display
    video_placeholder = st.empty()

    # Set display dimensions
    display_width = 640
    display_height = 360

    # Initialize frame counter and skip frame rate for speed
    frame_count = 0
    fps = video_file.get(cv2.CAP_PROP_FPS)
    skip_frames = 5  # Process every 3rd frame to speed up

    while True:
        # Skip frames to process faster
        for _ in range(skip_frames):
            ret, frame = video_file.read()
            if not ret:
                st.write("End of video.")
                break

        if not ret:
            break

        # Get predictions
        img_pred, predicted_texts, boxes = yolo.predictions(frame)

        # Convert BGR to RGB
        img_pred_rgb = cv2.cvtColor(img_pred, cv2.COLOR_BGR2RGB)

        # Draw bounding boxes and labels with color change based on condition
        for i, text in enumerate(predicted_texts):
            box = boxes[i]  # Assuming boxes are [x, y, w, h]
            x, y, w, h = box
            y += 35  # Shift the bounding box further below for more visibility
            # Set label color and font size based on object type
            color = (0, 0, 255) if "emergency" in text.lower() else (255, 0, 0)  # Red for emergency, blue otherwise
            font_size = 0.7
            font_thickness = 2

            # Draw bounding box
            cv2.rectangle(img_pred_rgb, (x, y), (x + w, y + h), color, 2)

            # Draw filled background rectangle for text label
            (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_size, font_thickness)
            cv2.rectangle(img_pred_rgb, (x, y + h + 5), (x + text_width, y + h + text_height + 15), (0, 0, 0), -1)

            # Put text label below the bounding box
            cv2.putText(img_pred_rgb, text, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), font_thickness)

        # Add timestamp with background for visibility
        timestamp = str(timedelta(seconds=int(frame_count / fps)))
        cv2.rectangle(img_pred_rgb, (5, 5), (170, 35), (0, 0, 0), -1)
        cv2.putText(img_pred_rgb, f'Time: {timestamp}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Resize the image for display
        img_resized = cv2.resize(img_pred_rgb, (display_width, display_height))

        # Show predicted image in placeholder
        video_placeholder.image(img_resized, caption='Predicted Video Frame', use_column_width=True)

        # Sidebar updates
        st.sidebar.write("### Predictions")
        st.sidebar.write("Detected Objects:")
        if predicted_texts:
            for text in predicted_texts:
                st.sidebar.write(text)
        else:
            st.sidebar.write("No objects detected.")
        st.sidebar.write(f"Current Time: {timestamp}")

        # Update frame counter
        frame_count += skip_frames

    # Release video capture
    video_file.release()

# Footer information
st.sidebar.write("### About")
st.sidebar.info("This app uses the YOLO model for real-time object detection. Upload a video to see predictions in action.")
