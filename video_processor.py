#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Video Processing Script for آساطير الغد (Legends of Tomorrow) Project
This script analyzes soccer skills from video inputs.
"""

import cv2
import numpy as np
import os
import time
from pathlib import Path
from ultralytics import YOLO

# Load YOLO models
def load_models():
    print("Loading YOLO models...")
    pose_model = YOLO('yolov8n-pose.pt')         # For keypoints
    ball_model = YOLO('yolov8n.pt')              # For detecting the ball
    return pose_model, ball_model

# ----- Skill 1: Jumping with Ball -----
def detect_ball_knee_contacts(video_path, pose_model, ball_model, frame_skip=2, distance_thresh=40, angle_thresh=60):
    """
    Detects contact between knees and ball in a soccer video
    
    Args:
        video_path (str): Path to the video file
        pose_model: YOLO pose detection model
        ball_model: YOLO object detection model
        frame_skip (int): Process every nth frame
        distance_thresh (float): Maximum distance to consider as contact
        angle_thresh (float): Maximum knee angle to consider as contact
        
    Returns:
        int: Score from 0-5 based on number of contacts
    """
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    touch_count = 0
    successful_touches = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_skip != 0:
            frame_idx += 1
            continue

        ball_results = ball_model(frame)[0]
        ball_pos = None
        for box, cls in zip(ball_results.boxes.xyxy, ball_results.boxes.cls):
            if int(cls) == 32:  # Class 32 is sports ball in COCO
                x1, y1, x2, y2 = map(int, box)
                ball_pos = ((x1 + x2) // 2, (y1 + y2) // 2)
                break

        pose_results = pose_model(frame)[0]
        if pose_results.keypoints is not None and pose_results.keypoints.xy.shape[0] > 0:
            keypoints = pose_results.keypoints.xy.cpu().numpy()[0]
            if keypoints.shape[0] >= 17:
                hip = keypoints[11]
                knee = keypoints[13]
                ankle = keypoints[15]

                def angle(a, b, c):
                    a, b, c = np.array(a), np.array(b), np.array(c)
                    ang = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
                    return np.abs(np.degrees(ang)) % 180

                knee_angle = angle(hip, knee, ankle)

                if ball_pos:
                    dist = np.linalg.norm(np.array(ball_pos) - np.array(knee))
                    if dist < distance_thresh and knee_angle < angle_thresh:
                        touch_count += 1
                        successful_touches.append({
                            "frame": frame_idx, 
                            "distance": round(dist, 1), 
                            "angle": round(knee_angle, 1)
                        })

        frame_idx += 1

    cap.release()
    score = min(5, touch_count)
    return score

# ----- Skill 2: Running with Ball -----
def evaluate_running_with_ball(video_path, pose_model, ball_model, frame_skip=2, min_ball_distance=30):
    """
    Evaluates running with ball skill from video
    
    Args:
        video_path (str): Path to the video file
        pose_model: YOLO pose detection model
        ball_model: YOLO object detection model
        frame_skip (int): Process every nth frame
        min_ball_distance (float): Minimum distance to consider ball controlled
        
    Returns:
        int: Score from 0-5 based on running speed while controlling ball
    """
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    distances = []
    prev_mid_hip = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_skip != 0:
            frame_idx += 1
            continue

        ball_results = ball_model(frame)[0]
        ball_pos = None
        for box, cls in zip(ball_results.boxes.xyxy, ball_results.boxes.cls):
            if int(cls) == 32:
                x1, y1, x2, y2 = map(int, box)
                ball_pos = ((x1 + x2) // 2, (y1 + y2) // 2)
                break

        pose_results = pose_model(frame)[0]
        if pose_results.keypoints is not None and pose_results.keypoints.xy.shape[0] > 0:
            keypoints = pose_results.keypoints.xy.cpu().numpy()[0]
            if keypoints.shape[0] >= 17:
                mid_hip = (keypoints[11] + keypoints[12]) / 2

                if ball_pos is not None:
                    ball_distance = np.linalg.norm(np.array(mid_hip) - np.array(ball_pos))
                    if ball_distance < min_ball_distance:
                        if prev_mid_hip is not None:
                            dx = mid_hip[0] - prev_mid_hip[0]
                            dy = mid_hip[1] - prev_mid_hip[1]
                            dist = np.sqrt(dx**2 + dy**2)
                            distances.append(dist)
                        prev_mid_hip = mid_hip

        frame_idx += 1

    cap.release()
    avg_speed = np.mean(distances) if distances else 0
    score = min(5, int(avg_speed * 10))
    return score

# ----- Skill 3: Passing -----
def evaluate_passing(video_path, pose_model, ball_model, frame_skip=2, ball_distance_thresh=100):
    """
    Evaluates passing skill from video
    
    Args:
        video_path (str): Path to the video file
        pose_model: YOLO pose detection model
        ball_model: YOLO object detection model
        frame_skip (int): Process every nth frame
        ball_distance_thresh (float): Distance threshold for pass detection
        
    Returns:
        int: Score from 0-5 based on successful passes
    """
    cap = cv2.VideoCapture(video_path)
    frame_idx = 0
    pass_attempts = 0
    successful_passes = 0
    previous_ball_pos = None
    previous_mid_ankle = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_skip != 0:
            frame_idx += 1
            continue

        ball_results = ball_model(frame)[0]
        ball_pos = None
        for box, cls in zip(ball_results.boxes.xyxy, ball_results.boxes.cls):
            if int(cls) == 32:
                x1, y1, x2, y2 = map(int, box)
                ball_pos = ((x1 + x2) // 2, (y1 + y2) // 2)
                break

        pose_results = pose_model(frame)[0]
        if pose_results.keypoints is not None and pose_results.keypoints.xy.shape[0] > 0:
            keypoints = pose_results.keypoints.xy.cpu().numpy()[0]
            if keypoints.shape[0] >= 17:
                left_ankle = keypoints[15]
                right_ankle = keypoints[16]
                mid_ankle = (left_ankle + right_ankle) / 2

                if previous_ball_pos and ball_pos:
                    ball_move = np.linalg.norm(np.array(ball_pos) - np.array(previous_ball_pos))
                    ankle_to_ball = np.linalg.norm(np.array(ball_pos) - mid_ankle)
                    if ball_move > 20 and ankle_to_ball > ball_distance_thresh:
                        pass_attempts += 1
                        if ball_move < 150:
                            successful_passes += 1

                previous_ball_pos = ball_pos
                previous_mid_ankle = mid_ankle

        frame_idx += 1

    cap.release()
    pass_score = min(5, successful_passes)
    return pass_score

def process_video(video_path, output_path=None):
    """
    Process a soccer skills video and evaluate multiple skills
    
    Args:
        video_path (str): Path to the input video
        output_path (str, optional): Path to save evaluation results
        
    Returns:
        dict: Results and scores for different skills
    """
    print(f"Processing video: {video_path}")
    start_time = time.time()
    
    # Load models
    pose_model, ball_model = load_models()
    
    # Evaluate different skills
    print("🏃‍♂️ Evaluating jumping with ball...")
    jump_score = detect_ball_knee_contacts(video_path, pose_model, ball_model)
    
    print("🏃‍♂️ Evaluating running with ball...")
    running_score = evaluate_running_with_ball(video_path, pose_model, ball_model)
    
    print("⚽️ Evaluating passing...")
    passing_score = evaluate_passing(video_path, pose_model, ball_model)
    
    # Calculate overall score
    overall_score = (jump_score + running_score + passing_score) / 3
    
    # Compile results
    results = {
        "jump_score": jump_score,
        "running_score": running_score,
        "passing_score": passing_score,
        "overall_score": overall_score,
        "processing_time": time.time() - start_time
    }
    
    # Save results to file if output path provided
    if output_path:
        import json
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4)
    
    # Print results
    print("\n📊 Skill Evaluation Results:")
    print(f"✅ Jumping with Ball: {jump_score}/5")
    print(f"✅ Running with Ball: {running_score}/5")
    print(f"✅ Passing: {passing_score}/5")
    print(f"✅ Overall Score: {overall_score:.1f}/5")
    print(f"⏱ Processing Time: {results['processing_time']:.2f} seconds")
    
    return results

def main():
    """
    Main function to run when executed as a script
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Process a soccer skills video for the آساطير الغد project")
    parser.add_argument("input_video", help="Path to the input video file")
    parser.add_argument("--output", "-o", help="Path to save evaluation results")
    
    args = parser.parse_args()
    
    # Process the video
    results = process_video(
        args.input_video, 
        output_path=args.output
    )

if __name__ == "__main__":
    main() 