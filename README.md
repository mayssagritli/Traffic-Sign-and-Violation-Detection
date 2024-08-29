# Traffic Law Enforcement System Using YOLOv8

## Overview

This project implements a real-time traffic law enforcement system using computer vision and deep learning. It's capable of detecting traffic violations in real-time using a camera mounted on a vehicle. The system utilizes a YOLOv8 model for object detection, specifically targeting traffic signs and signals (Speed Limits, Red/Green Light, and Stop Sign).

## Features

- Real-time traffic sign and signal detection using YOLOv8
- Violation detection for speeding, running red lights, and ignoring stop signs
- Video recording of detected violations
- MySQL database integration for storing violation records and model performance metrics
- Performance comparison between YOLOv8 and a custom CNN model
- Dashboard for visualizing model training metrics and traffic violations data

## System Architecture

- YOLOv8 Model: Custom-trained object detection model
- Violation Detection Algorithm: Interprets detected objects and identifies traffic violations
- Real-time Processing System: Integrates the model with live camera feed
- Database: MySQL for storing violation records and model performance metrics
- Frontend Application: Built with OutSystems for data visualization

## Project Structure

- `main.py`: Main script for detecting traffic signs and processing video inputs
- `checker.py`: Handles traffic control logic and database interactions
- `YoloDetector.py`: Manages object detection using the YOLO model
- `YoloTraining.ipynb`: Jupyter Notebook for model training and evaluation
- `maintest_live_version.py`: Main script for detecting traffic sign and processing live feed
- `Dashboard/`: OutSystems dashboard for visualizing metrics and violations data

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/traffic-law-enforcement.git
   cd traffic-law-enforcement
   ```

2. Install dependencies:
   ```
   pip install ultralytics opencv-python mysql-connector-python
   ```

3. Set up the MySQL database using the provided schema in the documentation.

4. Configure the database connection in `checker.py`.

5. Run the main application:
   for video input:
   ```
   python maintest.py 
   ```
   for live feed:
   python maintest_live_version

## Usage

The system can process live camera feed or video files for traffic violation detection. To use a video file instead of live feed, modify the `video_path` parameter in `main.py`.

## Dashboard

The OutSystems dashboard provides visualization for:
- Model Training Metrics: Comparing YOLOv8 and CNN performance
- Traffic Violations: Detailed information about detected violations

## Future Improvements

1. Implement real-time speed detection
2. Enhance violation detection algorithms for higher accuracy
3. Train with additional datasets to detect cars and other signs

## Contributors

- Mayssa Gritli (Project Lead)
- Feres Baba (Improved Violation Detection Algorithms)
- Arafet Zouari (Supervisor)

## Acknowledgments
I want to thank my supervisor Arafet Zouari for his invaluable guidance and support throughout my internship.I truly appreciate all the time and effort he've invested in helping me succeed.
- Dataset source: Kaggle
- YOLOv8: Ultralytics
- OutSystems for dashboard development

For more detailed information, please refer to the full documentation.
