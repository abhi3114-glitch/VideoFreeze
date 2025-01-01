# VideoFreeze: Automatic Thumbnail Frame Selector

VideoFreeze is a local, privacy-focused application that automatically analyzes video files to identify the most aesthetically pleasing frame for use as a thumbnail. It utilizes computer vision heuristics to score frames based on photographic principles, ensuring high-quality results without uploading content to the cloud.

## Features

- **Sharpness Detection**: Utilizes Laplacian variance to identify and prioritize frames with the highest focus quality.
- **Face Clarity**: Detects faces using Haar Cascades, scoring them based on optimal size and visibility.
- **Brightness Balance**: Analyzes pixel intensity histograms to ensure frames are essentially exposed, avoiding overexposure or underexposure.
- **Composition Analysis**: Evaluates frames against the Rule of Thirds using edge detection to determine optimal visual balance.
- **Privacy Centric**: All processing is performed locally on the CPU. No video data is ever transmitted to external servers.
- **Configurable Scoring**: Users can adjust the weight of each aesthetic metric to tailor the selection process to their specific needs.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/abhi3114-glitch/VideoFreeze.git
    cd VideoFreeze
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:
    ```bash
    streamlit run app.py
    ```

2.  Upload a video file (supported formats: MP4, AVI, MOV, MKV).

3.  (Optional) Adjust analysis settings in the sidebar:
    -   **Sampling Rate**: Controls the number of frames analyzed per second. Higher values provide more precision but require longer processing times.
    -   **Weights**: Customize the importance of individual metrics (Sharpness, Face Clarity, Brightness, Composition).

4.  Click "Find Best Thumbnail" to begin the analysis.

5.  Preview the selected frame and download it as a high-resolution PNG or JPG.

## Technical Details

VideoFreeze samples the input video at a user-defined interval (default: 0.5 FPS) and applies four lightweight algorithms to each sampled frame:

1.  **Sharpness**: Measures the variance of the Laplacian of the image. Higher variance matches well with higher focus.
2.  **Face Score**: Scores frames based on the presence of faces. It penalizes frames with too many faces or faces that are too small or too large, favoring clear, portrait-style compositions.
3.  **Brightness**: Calculates the distribution of pixel intensities. It penalizes frames with significant clipping (pure black or pure white) or poor contrast.
4.  **Composition**: Uses Canny edge detection to identify salient regions and checks their alignment with the intersection points of a 3x3 grid (Rule of Thirds).

The final aesthetic score is a weighted average of these four individual metrics.

## Requirements

-   Python 3.8 or higher
-   OpenCV
-   Streamlit
-   NumPy
-   Pillow
-   SciPy

## Project Structure

-   `app.py`: Main entry point for the Streamlit user interface.
-   `analyzer/`: Contains the core computer vision algorithms.
    -   `sharpness.py`: Implements sharpness and focus scoring.
    -   `face_detector.py`: Implements face detection and clarity scoring.
    -   `brightness.py`: Implements exposure and histogram analysis.
    -   `composition.py`: Implements Rule of Thirds and composition scoring.
-   `export/`: Handles image export and metadata generation.
