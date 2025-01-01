
import cv2
import numpy as np
import os
import sys
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzer.frame_extractor import extract_frames
from analyzer.aesthetic_scorer import score_frame, find_best_frame
from export.frame_saver import save_frame
from export.metadata_generator import generate_metadata

def create_dummy_video(filename="test_video.mp4", duration=2, fps=30):
    """Create a simple dummy video for testing."""
    height, width = 480, 640
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    # Create frames with different characteristics
    for i in range(duration * fps):
        # Frame 1: Pure noise (low sharpness)
        if i < 15:
            frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        # Frame 2: Gradient (better)
        elif i < 30:
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                frame[y, :, :] = (y % 255, (i*5) % 255, 100)
        # Frame 3: White square (high brightness/contrast)
        else:
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.rectangle(frame, (100, 100), (300, 300), (255, 255, 255), -1)
            # Add a "face" (circle)
            cv2.circle(frame, (400, 200), 50, (200, 200, 200), -1)
            
        out.write(frame)
    
    out.release()
    return filename

def test_pipeline():
    print("Starting smoke test...")
    
    # 1. Create dummy video
    video_path = create_dummy_video()
    print(f"Created dummy video: {video_path}")
    
    try:
        # 2. Test Frame Extraction
        print("Testing frame extraction...")
        frames = extract_frames(video_path, fps=1.0)
        print(f"Extracted {len(frames)} frames")
        assert len(frames) > 0, "No frames extracted"
        
        # 3. Test Scoring
        print("Testing scoring...")
        for frame, ts in frames:
            scores = score_frame(frame)
            print(f"Frame at {ts}s scores: {scores}")
            
        # 4. Test Best Frame Selection
        print("Testing best frame selection...")
        idx, best_frame, ts, scores = find_best_frame(frames)
        print(f"Best frame found at index {idx} (timestamp: {ts}s)")
        
        # 5. Test Export
        print("Testing export...")
        export_dir = "test_output"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        save_path = save_frame(best_frame, output_path=os.path.join(export_dir, "best.jpg"), format="jpg")
        print(f"Saved frame to {save_path}")
        assert os.path.exists(save_path), "File not saved"
        
        # 6. Test Metadata
        print("Testing metadata generation...")
        meta_path = generate_metadata(
            video_path, 
            {'resolution': '640x480', 'duration': 2.0, 'fps': 30, 'total_frames': 60},
            ts, scores, len(frames), 0.5,
            output_path=os.path.join(export_dir, "metadata.txt")
        )
        print(f"Saved metadata to {meta_path}")
        assert os.path.exists(meta_path), "Metadata not saved"
        
        print("\n✅ SMOKE TEST PASSED: All components functioning correctly.")
        
    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e
        
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists("test_output"):
            shutil.rmtree("test_output")

if __name__ == "__main__":
    test_pipeline()
