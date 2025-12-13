import script_processor_for_video as spv
import clip_maker_sora as clm
import re
import os
import glob

# Sort in the way that "file10" is after "file1".
def numerical_sort(value):
    numbers = re.findall(r'\d+', os.path.basename(value))
    return int(numbers[0]) if numbers else 0


def loop(scenes, 
         image_folder = "./intermediate_files/images", 
         clip_folder = "./intermediate_files/clips"):
    
    # Clip Maker loop
    image_files = sorted(glob.glob(os.path.join(image_folder, "*.png")), key=numerical_sort)
    if not image_files:
        raise FileNotFoundError(f"No mp4 videos found in '{image_folder}'")

    for i, image_path in enumerate(image_files):
        print(f"Making clip for image {i+1}: {image_path}\n")
        print(f"Prompt sent: {scenes[i]}\n")
        clm.make(image_path=image_path, prompt=scenes[i], output_folder=clip_folder)

