# DINO-X Video Detection Demo

This application demonstrates real-time object detection, segmentation, pose estimation, and more using the DINO-X API on video streams.

## Features

- Real-time object detection from webcam or video files
- Support for text prompts or universal detection
- Multiple detection targets: bounding boxes, masks, pose keypoints, hand keypoints
- Visual display of detection results
- Region-based visual language descriptions
- Adjustable confidence thresholds
- Detection history tracking

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your DINO-X API token:
   ```
   DINOX_API_TOKEN=your_api_token_here
   ```

## Usage

Run the Streamlit application:

```
streamlit run app.py
```

Then open your browser and navigate to the URL displayed in the terminal (usually http://localhost:8501).

## Configuration

- Select input source (webcam or video file)
- Choose detection mode (text prompt or universal)
- Enter text prompts for specific objects
- Select detection targets (bounding boxes, masks, pose keypoints, hand keypoints)
- Adjust confidence threshold
- Toggle visualization options

## Notes

- The application processes frames at regular intervals to avoid API rate limiting
- Detection results are cached to improve performance
- For best results, ensure good lighting conditions when using webcam input 