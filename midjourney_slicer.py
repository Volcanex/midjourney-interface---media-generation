from PIL import Image
import os

def slice_image(file_path):
    # Load image
    img = Image.open(file_path)

    # Get dimensions
    width, height = img.size

    # Calculate slices
    slices = [
        (0, 0, width//2, height//2),  # Upper left
        (width//2, 0, width, height//2),  # Upper right
        (0, height//2, width//2, height),  # Lower left
        (width//2, height//2, width, height)  # Lower right
    ]

    # Slice image and save each slice to a new file
    script_directory = os.path.dirname(os.path.abspath(__file__))
    new_folder = os.path.join(script_directory, "sliced_images")
    os.makedirs(new_folder, exist_ok=True)
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    for i, slice in enumerate(slices):
        # Slice image
        slice_img = img.crop(slice)

        # Save sliced image to new file
        slice_file_path = os.path.join(new_folder, f"{file_name}_slice{i+1}.jpg")
        slice_img.save(slice_file_path)

    print(f"Image sliced and saved to {new_folder} folder.")

def slice_image_alt(image_path):
    img = Image.open(image_path)
    width, height = img.size

    # Calculate the size of a single quadrant
    quad_width, quad_height = width // 2, height // 2

    # Top-left quadrant
    img_tl = img.crop((0, 0, quad_width, quad_height))
    img_tl.save(image_path)

    # Save other quadrants in the "waste" folder
    waste_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'waste')
    os.makedirs(waste_folder, exist_ok=True)

    # Top-right quadrant
    img_tr = img.crop((quad_width, 0, width, quad_height))
    img_tr.save(os.path.join(waste_folder, 'tr_' + os.path.basename(image_path)))

    # Bottom-left quadrant
    img_bl = img.crop((0, quad_height, quad_width, height))
    img_bl.save(os.path.join(waste_folder, 'bl_' + os.path.basename(image_path)))

    # Bottom-right quadrant
    img_br = img.crop((quad_width, quad_height, width, height))
    img_br.save(os.path.join(waste_folder, 'br_' + os.path.basename(image_path)))
