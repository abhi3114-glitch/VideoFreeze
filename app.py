import streamlit as st
import tempfile
import os
import time
from pathlib import Path
import cv2
from PIL import Image
import numpy as np

# Import our custom modules
from analyzer.frame_extractor import extract_frames, get_video_info
from analyzer.aesthetic_scorer import score_all_frames, find_best_frame
from export.frame_saver import save_frame
from export.metadata_generator import generate_metadata

# Page config
st.set_page_config(
    page_title="VideoFreeze - Aesthetic Thumbnail Selector",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    .score-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .metric-label {
        font-size: 14px;
        color: #555;
    }
    .highlight {
        color: #ff4b4b; 
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🎬 VideoFreeze")
    st.markdown("### Automatic Aesthetic Thumbnail Selector")
    st.markdown("Upload a video to automatically find the most aesthetic frame for your thumbnail.")

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.subheader("Analysis")
        fps_sampling = st.slider(
            "Sampling Rate (FPS)", 
            min_value=0.1, 
            max_value=2.0, 
            value=0.5, 
            step=0.1,
            help="How many frames to analyze per second of video. Higher = slower but more precise."
        )
        
        st.subheader("Scoring Weights")
        w_sharpness = st.slider("Sharpness", 0.0, 1.0, 0.30)
        w_face = st.slider("Face Clarity", 0.0, 1.0, 0.25)
        w_brightness = st.slider("Brightness", 0.0, 1.0, 0.20)
        w_composition = st.slider("Composition", 0.0, 1.0, 0.25)
        
        # Normalize weights
        total_w = w_sharpness + w_face + w_brightness + w_composition
        if total_w > 0:
            weights = {
                'sharpness': w_sharpness / total_w,
                'face_clarity': w_face / total_w,
                'brightness': w_brightness / total_w,
                'composition': w_composition / total_w
            }
        else:
            weights = {
                'sharpness': 0.25,
                'face_clarity': 0.25,
                'brightness': 0.25,
                'composition': 0.25
            }
            
        st.info("Weights define what 'aesthetic' means to you.")

    # Main area
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'mov', 'avi', 'mkv'])

    if uploaded_file is not None:
        # Save to temp file
        tfile = tempfile.NamedTemporaryFile(delete=False) 
        tfile.write(uploaded_file.read())
        video_path = tfile.name
        
        # Show video details
        try:
            video_info = get_video_info(video_path)
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Resolution", video_info['resolution'])
            col2.metric("Duration", f"{video_info['duration']:.1f}s")
            col3.metric("FPS", f"{video_info['fps']:.0f}")
            estimated_frames = int(video_info['duration'] * fps_sampling)
            col4.metric("Est. Frames to Analyze", estimated_frames)
            
            # Analyze button
            if st.button("🔍 Find Best Thumbnail", type="primary"):
                with st.spinner(f"Analyzing approximately {estimated_frames} frames..."):
                    start_time = time.time()
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    def update_progress(current, total):
                        progress = min(current / total, 1.0)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing frame {current}/{total}")
                    
                    # Extract frames
                    status_text.text("Extracting frames...")
                    frames = extract_frames(video_path, fps=fps_sampling)
                    
                    # Analyze and find best frame
                    status_text.text("Scoring aesthetic quality...")
                    best_idx, best_img, best_ts, best_scores = find_best_frame(
                        frames, 
                        weights=weights,
                        progress_callback=update_progress
                    )
                    
                    processing_time = time.time() - start_time
                    status_text.text("Done!")
                    time.sleep(0.5)
                    status_text.empty()
                    progress_bar.empty()
                    
                    # Store results in session state
                    st.session_state.processed = True
                    st.session_state.best_img = best_img
                    st.session_state.best_ts = best_ts
                    st.session_state.best_scores = best_scores
                    st.session_state.video_path = video_path
                    st.session_state.video_info = video_info
                    st.session_state.total_frames = len(frames)
                    st.session_state.processing_time = processing_time
                    st.session_state.video_name = uploaded_file.name

        except Exception as e:
            st.error(f"Error loading video: {str(e)}")
            return

    # Display results if available
    if 'processed' in st.session_state and st.session_state.processed:
        st.divider()
        st.subheader("🏆 Best Thumbnail Found")
        
        # Display Best Frame
        # Convert BGR to RGB for Streamlit/Pillow
        best_img_rgb = cv2.cvtColor(st.session_state.best_img, cv2.COLOR_BGR2RGB)
        st.image(best_img_rgb, caption=f"Timestamp: {st.session_state.best_ts:.2f}s", use_column_width=True)
        
        # Display Scores
        scores = st.session_state.best_scores
        st.subheader("📊 Aesthetic Score Breakdown")
        
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        
        with sc1:
            st.metric("Overall Score", f"{scores['overall']:.1f}/100")
        with sc2:
            st.metric("Sharpness", f"{scores['sharpness']:.1f}/100")
        with sc3:
            st.metric("Face Clarity", f"{scores['face_clarity']:.1f}/100", f"{scores['face_count']} faces")
        with sc4:
            st.metric("Brightness", f"{scores['brightness']:.1f}/100")
        with sc5:
            st.metric("Composition", f"{scores['composition']:.1f}/100")
            
        # Export Options
        st.divider()
        st.subheader("💾 Export Options")
        
        col_ex1, col_ex2 = st.columns([1, 2])
        
        with col_ex1:
            export_format = st.radio("Format", ["PNG", "JPG"])
            
            # Prepare download
            # We save to a temp buffer for the download button
            from io import BytesIO
            
            img_pil = Image.fromarray(best_img_rgb)
            buf = BytesIO()
            
            if export_format == "PNG":
                img_pil.save(buf, format="PNG")
                mime_type = "image/png"
                ext = "png"
            else:
                img_pil.save(buf, format="JPEG", quality=95)
                mime_type = "image/jpeg"
                ext = "jpg"
                
            byte_im = buf.getvalue()
            
            base_name = os.path.splitext(st.session_state.video_name)[0]
            dl_name = f"{base_name}_thumbnail_{int(st.session_state.best_ts)}s.{ext}"
            
            st.download_button(
                label=f"⬇️ Download {export_format}",
                data=byte_im,
                file_name=dl_name,
                mime=mime_type,
            )
            
        with col_ex2:
            st.info(f"Analyzed {st.session_state.total_frames} frames in {st.session_state.processing_time:.2f} seconds.")
            
            # Option to save metadata locally if running locally
            if st.button("Save to 'exports' folder (Image + Metadata)"):
                try:
                    # Create export dir
                    from export.frame_saver import create_export_directory, save_frame
                    from export.metadata_generator import generate_metadata
                    
                    export_dir = create_export_directory()
                    
                    # Save image
                    save_path = os.path.join(export_dir, dl_name)
                    saved_img = save_frame(st.session_state.best_img, save_path, format=export_format.lower())
                    
                    # Save metadata
                    meta_path = generate_metadata(
                        video_path=st.session_state.video_name,
                        video_info=st.session_state.video_info,
                        frame_timestamp=st.session_state.best_ts,
                        scores=st.session_state.best_scores,
                        total_frames_analyzed=st.session_state.total_frames,
                        processing_time=st.session_state.processing_time,
                        output_path=os.path.join(export_dir, f"{base_name}_metadata.txt")
                    )
                    
                    st.success(f"Saved to: {export_dir}")
                except Exception as e:
                    st.error(f"Error saving locally: {str(e)}")

if __name__ == "__main__":
    main()
