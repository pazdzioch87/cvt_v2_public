import os
import cv2
import time
import supervision as sv
import numpy as np
import threading
import queue
from ultralytics import YOLO
from i_process_frame_instance import frame_processor
from config import config
from state import app_state

FPS = 1/30

def run_one_time_analysis(frame):
    """Run one-time frame analysis."""
    try:
        frame_processor.process_frame(frame)
    except Exception as e:
        print(f"Error in frame analysis: {e}")
    finally:
        # Reset the trigger flag
        app_state.set('analysis_triggered', False)

def process_frame_with_yolo(frame, model, box_annotator):
    """Process a frame with YOLO model and return annotated frame and detections."""
    results = model(frame)
    result = results[0]
    detections = sv.Detections(
        xyxy=result.boxes.xyxy.cpu().numpy(),
        confidence=result.boxes.conf.cpu().numpy(),
        class_id=result.boxes.cls.cpu().numpy().astype(int)
    )
    
    # Filter detections for person and vehicles
    mask = np.isin(detections.class_id, [0, 1, 2, 3, 5, 7])
    detections.xyxy = detections.xyxy[mask]
    detections.confidence = detections.confidence[mask]
    detections.class_id = detections.class_id[mask]

    if len(detections.xyxy) > 0:
        labels = [f"{result.names[class_id]} {confidence:0.2f}"
                  for class_id, confidence
                  in zip(detections.class_id, detections.confidence)]
        detections.labels = labels

        frame = box_annotator.annotate(
            scene=frame,
            detections=detections
        )

        # Check if we should trigger analysis (person detected and not already triggered)
        analysis_triggered = app_state.get('analysis_triggered', False)
        if 0 in detections.class_id and not analysis_triggered:
            app_state.set('analysis_triggered', True)
            # Run analysis in a separate thread to not block video processing
            threading.Thread(target=run_one_time_analysis, args=(frame,), daemon=True).start()
    
    return frame, detections

def yolo_processing_thread(processed_frame_queue, model, box_annotator, stop_event):
    """Thread function for processing frames with YOLO."""
    while not stop_event.is_set():
        latest_frame = app_state.get('latest_frame')
        if latest_frame is not None:
            frame = latest_frame.copy()
            # Clear the latest frame to allow new frames
            app_state.set('latest_frame', None)
            try:
                processed_frame, _ = process_frame_with_yolo(frame, model, box_annotator)
                processed_frame_queue.put(processed_frame)
            except Exception as e:
                print(f"Error processing frame: {e}")
        else:
            time.sleep(0.01)  # Small delay to prevent busy waiting

def analyze_video(rtmp_url):
    """Main video analysis function."""
    # Check environment and transform URL based on environment
    if config.is_development:
        # Use localhost for local development
        print("Running in development mode")
    else:
        # Use container name in production
        rtmp_url = rtmp_url.replace("localhost", config.SRS_HOST)
        print("Running in production mode")
    print(f"Connecting to RTMP stream: {rtmp_url}")
    
    cap = cv2.VideoCapture(rtmp_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to limit delay
    
    if not cap.isOpened():
        raise Exception(f"Failed to connect to RTMP stream: {rtmp_url}")

    processed_frame_queue = queue.Queue(maxsize=3)
    model = YOLO(config.YOLO_MODEL_PATH, verbose=config.YOLO_VERBOSE)
    box_annotator = sv.BoxAnnotator(thickness=2)

    # Thread synchronization primitives
    stop_event = threading.Event()
    
    # Clear any previous state
    app_state.set('latest_frame', None)
    app_state.set('analysis_triggered', False)

    t = threading.Thread(
        target=yolo_processing_thread, 
        args=(processed_frame_queue, model, box_annotator, stop_event),
        daemon=True
    )
    t.start()

    analysis_enabled = False
    try:
        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Update the latest frame if queue is not full and no frame is waiting
            if not processed_frame_queue.full() and app_state.get('latest_frame') is None:
                app_state.set('latest_frame', frame.copy())

            # Display processed frames if available
            if not processed_frame_queue.empty():
                processed_frame_for_display = processed_frame_queue.get()
                # NOTE: We're keeping the cv2.imshow for now as requested, but in a production
                # environment, this should be removed or made configurable
                cv2.imshow("YOLO Analyzed Frame", processed_frame_for_display)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            if key == ord('w'):
                time.sleep(3)
            if key == ord('a'):
                analysis_enabled = not analysis_enabled

    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Error during video analysis: {e}")
    finally:
        # Cleanup
        stop_event.set()
        if t.is_alive():
            t.join(timeout=5)  # Wait up to 5 seconds for thread to finish

        cap.release()
        cv2.destroyAllWindows()
        print("Video analysis stopped.")
