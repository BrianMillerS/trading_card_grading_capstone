import os
from PIL import Image

def flip_images_in_directory(directory):
    # Get all subdirectories within the main directory
    subdirectories = [subdir for subdir in os.listdir(directory) if os.path.isdir(os.path.join(directory, subdir))]

    # Iterate over the subdirectories
    for subdir in subdirectories:
        subdir_path = os.path.join(directory, subdir)

        # Get all .jpg files in the subdirectory
        image_files = [file for file in os.listdir(subdir_path) if file.endswith('.jpg')]

        # Iterate over the image files
        for image_file in image_files:
            # Open the image file
            image_path = os.path.join(subdir_path, image_file)
            image = Image.open(image_path)

            # Flip the image horizontally
            flipped_image = image.transpose(Image.FLIP_LEFT_RIGHT)

            # Save the flipped image with a new filename
            flipped_filename = os.path.splitext(image_file)[0] + '_flipped.jpg'
            save_path = os.path.join(subdir_path, flipped_filename)
            flipped_image.save(save_path)

    print("All images flipped and saved for directory: {}".format(subdir))

# Get the current working directory
current_directory = os.getcwd()

# Call the function to flip images in each subfolder of the current working directory
flip_images_in_directory(current_directory)
