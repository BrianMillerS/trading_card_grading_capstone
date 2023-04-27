import pandas as pd
import numpy as np
import cv2

def augment_image(image_path, output_prefix):
    
    # Load the original image
    image = cv2.imread(image_path)

    # Perform horizontal flip
    flipped_image = cv2.flip(image, 1)

    # Define the rotation matrix for 20 degrees clockwise rotation
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M_clockwise = cv2.getRotationMatrix2D(center, -10, 1.0)
    rotated_image_clockwise = cv2.warpAffine(image, M_clockwise, (w, h))

    # Define the rotation matrix for 20 degrees counterclockwise rotation
    M_counterclockwise = cv2.getRotationMatrix2D(center, 10, 1.0)
    rotated_image_counterclockwise = cv2.warpAffine(image, M_counterclockwise, (w, h))

    # Save the augmented images
    cv2.imwrite(output_prefix + '_flipped.jpg', flipped_image)
    cv2.imwrite(output_prefix + '_rotated_clockwise.jpg', rotated_image_clockwise)
    cv2.imwrite(output_prefix + '_rotated_counterclockwise.jpg', rotated_image_counterclockwise)

# Example usage
augment_image('/Users/brianmiller/Desktop/test_background/card1_PSA1.jpg', '/Users/brianmiller/Desktop/test_background/card1_PSA1')