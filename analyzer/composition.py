"""
Composition Analyzer Module

Analyzes frame composition using rule of thirds and edge detection.
"""

import cv2
import numpy as np


def calculate_composition_score(frame: np.ndarray) -> float:
    """
    Calculate composition score based on rule of thirds.
    
    Uses edge detection to find salient regions and checks if they align
    with rule-of-thirds intersection points.
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        Composition score (0-100)
    """
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    
    # Apply edge detection to find salient regions
    edges = cv2.Canny(gray, 50, 150)
    
    # Calculate rule of thirds grid points
    # The grid divides the image into 3x3 sections
    # Intersection points are at 1/3 and 2/3 positions
    third_h = height // 3
    third_w = width // 3
    
    # Define rule of thirds intersection points (4 points)
    rot_points = [
        (third_w, third_h),           # Top-left intersection
        (2 * third_w, third_h),       # Top-right intersection
        (third_w, 2 * third_h),       # Bottom-left intersection
        (2 * third_w, 2 * third_h)    # Bottom-right intersection
    ]
    
    # Create interest map using edge density
    # Divide edges into grid cells and calculate density
    grid_size = 20  # Size of each grid cell for edge density calculation
    interest_map = np.zeros((height // grid_size, width // grid_size))
    
    for i in range(0, height - grid_size, grid_size):
        for j in range(0, width - grid_size, grid_size):
            cell = edges[i:i+grid_size, j:j+grid_size]
            interest_map[i//grid_size, j//grid_size] = np.sum(cell)
    
    # Find regions with high edge density (points of interest)
    # Normalize interest map
    if interest_map.max() > 0:
        interest_map = interest_map / interest_map.max()
    
    # Calculate score based on interest near rule of thirds points
    total_score = 0
    check_radius = max(height, width) // 12  # Radius around each RoT point to check
    
    for rot_x, rot_y in rot_points:
        # Calculate edge density in region around this RoT point
        y1 = max(0, rot_y - check_radius)
        y2 = min(height, rot_y + check_radius)
        x1 = max(0, rot_x - check_radius)
        x2 = min(width, rot_x + check_radius)
        
        region = edges[y1:y2, x1:x2]
        
        if region.size > 0:
            edge_density = np.sum(region) / region.size
            # Normalize and add to score (max 25 points per RoT point)
            total_score += min(25, edge_density / 10)
    
    # Additional scoring based on overall balance
    # Check if edges are distributed across the frame
    left_edges = np.sum(edges[:, :width//2])
    right_edges = np.sum(edges[:, width//2:])
    top_edges = np.sum(edges[:height//2, :])
    bottom_edges = np.sum(edges[height//2:, :])
    
    # Calculate balance (lower difference = better balance)
    if left_edges + right_edges > 0:
        lr_balance = 1 - abs(left_edges - right_edges) / (left_edges + right_edges)
    else:
        lr_balance = 0
    
    if top_edges + bottom_edges > 0:
        tb_balance = 1 - abs(top_edges - bottom_edges) / (top_edges + bottom_edges)
    else:
        tb_balance = 0
    
    # Penalize completely centered compositions (often less interesting)
    center_region = edges[third_h:2*third_h, third_w:2*third_w]
    if edges.sum() > 0:
        center_weight = center_region.sum() / edges.sum()
        center_penalty = max(0, (center_weight - 0.5) * 20) if center_weight > 0.5 else 0
    else:
        center_penalty = 0
    
    # Combine scores
    balance_score = (lr_balance + tb_balance) * 10
    final_score = total_score + balance_score - center_penalty
    
    return float(min(100, max(0, final_score)))


def visualize_rule_of_thirds(frame: np.ndarray) -> np.ndarray:
    """
    Draw rule of thirds grid on frame for visualization.
    
    Args:
        frame: Input frame (BGR)
        
    Returns:
        Frame with rule of thirds grid overlay
    """
    result = frame.copy()
    height, width = frame.shape[:2]
    
    # Calculate grid lines
    third_h = height // 3
    third_w = width // 3
    
    # Draw horizontal lines
    cv2.line(result, (0, third_h), (width, third_h), (0, 255, 0), 2)
    cv2.line(result, (0, 2*third_h), (width, 2*third_h), (0, 255, 0), 2)
    
    # Draw vertical lines
    cv2.line(result, (third_w, 0), (third_w, height), (0, 255, 0), 2)
    cv2.line(result, (2*third_w, 0), (2*third_w, height), (0, 255, 0), 2)
    
    # Draw intersection points
    for x in [third_w, 2*third_w]:
        for y in [third_h, 2*third_h]:
            cv2.circle(result, (x, y), 8, (0, 255, 0), -1)
    
    return result
