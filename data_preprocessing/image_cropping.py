import os
from PIL import Image

input_path = r'C:\Users\Seanw\OneDrive\Desktop\Capstone Project\images_3k\images_3k'
output_path = os.path.join(input_path, 'cropped_images')

# Define the target pixel size for scaling images
target_pixel_size = 400

for filename in os.listdir(input_path):
    if filename.endswith(".JPG"):
        with Image.open(os.path.join(input_path, filename)) as im:
            # Get the dimensions of the image
            width, height = im.size

            # Skip images smaller than target pixel size
            if width < target_pixel_size or height < target_pixel_size:
                print(f"Skipping image '{filename}' as its dimensions are smaller than target pixel size.")
                continue

            # Step 1: Rotate the image if the x-axis is greater than the y-axis
            if width > height:
                im = im.rotate(90, expand=True)  # Rotate the image by 90 degrees clockwise
                width, height = im.size  # Update the image dimensions after rotation

            # Step 2: Scale the image to the target pixel size while maintaining its aspect ratio
            aspect_ratio = width / height
            if width > target_pixel_size or height > target_pixel_size:
                new_width = 400
                new_height = 800
                im = im.resize((new_width, new_height))
                width, height = im.size  # Update the image dimensions after resizing

            # Step 3: Crop the image in the same way
            # Define the top and bottom crop points
            crop_top = int(height / 5.5)
            crop_bottom = height

            # Calculate the maximum allowed cropping height as 1/6th of the image height
            max_crop_height = int(height / 5.5)

            # Check if the red rectangular label is present
            for y in range(new_height):
                # Update the x-axis index based on the resized image
                x = new_width // 2
                r, g, b = im.getpixel((x, y))
                if r > 100 and g < 0 and b < 0:
                    # If the red rectangular label is present, update the crop points
                    if y > height // 2:
                        # Crop the top of the image
                        crop_top = 0  # Reset the top crop point to 0
                        break
                    else:
                        # Crop the bottom of the image
                        crop_top = max(y + max_crop_height, crop_top)

            # Ensure the crop point does not exceed the image height
            crop_top = min(crop_top, height - 1)

            # Crop the image
            cropped_img = im.crop((0, crop_top, new_width, crop_bottom))

            # Save the cropped image
            file_name = os.path.splitext(filename)[0] + "_cropped.JPG"
            cropped_img.save(os.path.join(output_path, file_name))
