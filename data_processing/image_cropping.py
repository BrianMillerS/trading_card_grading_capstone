import os
from PIL import Image

# make a list of folders to go through and crop the images
parent_dir = "/Users/brianmiller/Desktop/trading_card_data/final_10k"
output_dir = "/Users/brianmiller/Desktop/trading_card_data/final10k_cropped"
folder_names = ["psa1", "psa2", "psa3", "psa4", "psa5", "psa6", "psa7", "psa8", "psa9", "psa10"]


list_of_folders = [parent_dir + '/' + i for i in folder_names]

# Define the target pixel size for scaling images
target_pixel_size = 400

for folder_path in list_of_folders:
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.jpg'):
            with Image.open(os.path.join(folder_path, filename)) as im:
                
                # Convert the image to RGB mode
                im = im.convert("RGB")
            
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

                # Step 2: Crop the image in the same way
                # Define the top and bottom crop points
                crop_top = int(height / 5)
                crop_bottom = height
                # Calculate the maximum allowed cropping height as 1/5th of the image height
                max_crop_height = int(height / 5)
                # Check if the red rectangular label is present
                for y in range(height):
                    # Update the x-axis index based on the resized image
                    x = width // 2
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
                cropped_img = im.crop((0, crop_top, width, crop_bottom))

                # Step 3: Scale the image to the target pixel size while maintaining its aspect ratio
                cropped_width, cropped_height = cropped_img.size
                if cropped_width > target_pixel_size or cropped_height > target_pixel_size:
                    new_width = 400
                    new_height = int(new_width * (cropped_height / cropped_width))
                    cropped_img = cropped_img.resize((new_width, new_height))

                # Save the cropped and resized image
                file_name = os.path.splitext(filename)[0] + "_cropped.jpg"
                cropped_img.save(os.path.join(output_dir, file_name))
