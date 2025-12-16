from openai import OpenAI
import sys
import time
from helper_functions import image_operations
from datetime import datetime
import re
import os
import glob

with open("api_key.txt", "r") as file:
    api_key = file.read()
client = OpenAI(api_key = api_key)

def make_one(image_path, prompt, output_folder=None):
    # Resize images to feed Sora.
    image_path = image_operations.resize_image(image_path, width=1280, height=720)

    video = client.videos.create(
        model="sora-2",
        prompt=prompt,
        seconds=4,
        size="1280x720",
        input_reference=(image_path, open(image_path, "rb"), "image/png"),
    )

    print("Video generation started:\n", video)

    progress = getattr(video, "progress", 0)
    bar_length = 30

    while video.status in ("in_progress", "queued"):
        # Refresh status
        video = client.videos.retrieve(video.id)
        progress = getattr(video, "progress", 0)

        filled_length = int((progress / 100) * bar_length)
        bar = "=" * filled_length + "-" * (bar_length - filled_length)
        status_text = "Queued" if video.status == "queued" else "Processing"

        sys.stdout.write(f"{status_text}: [{bar}] {progress:.1f}%\n")
        sys.stdout.flush()
        time.sleep(2)

    # Move to next line after progress loop
    sys.stdout.write("")

    if video.status == "failed":
        message = getattr(
            getattr(video, "error", None), "message", "Video generation failed"
        )
        print(message)
    else:
        print("Video generation completed:\n", video)
        print("Downloading video content...")

        content = client.videos.download_content(video.id, variant="video")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_folder is not None:
            content.write_to_file(f"{output_folder}/video_{timestamp}.mp4")
        else:
            content.write_to_file(f"video_{timestamp}.mp4")

        print("Video saved.\n")

# Sort in the way that "file10" is after "file1".
def numerical_sort(value):
    numbers = re.findall(r'\d+', os.path.basename(value))
    return int(numbers[0]) if numbers else 0

def make_many(scenes, image_folder="./intermediate_files/images", clip_folder="./intermediate_files/clips"):
    # Clip Maker loop
    image_files = sorted(glob.glob(os.path.join(image_folder, "*.png")), key=numerical_sort)
    if not image_files:
        raise FileNotFoundError(f"No mp4 videos found in '{image_folder}'")

    for i, image_path in enumerate(image_files):
        print(f"Making clip for image {i+1}: {image_path}\n")
        print(f"Prompt sent: {scenes[i]}\n")
        make_one(image_path=image_path, prompt=scenes[i], output_folder=clip_folder)


# Run file to use the function one time.
if __name__ == "__main__":
    image_path = "./generated_image copy 10/shot_3.png"
    # image_path = "./intermediate_files/images/shot_15.png"
    # output_folder = "./intermediate_files/clips"
    prompt="""Scene 3
    - Plot: Outside a glittering Broadway restaurant at night, Soapy stands on the curb with determination, studying the large plate-glass windows that glow with dinner-lit warmth. Pedestrians in fine coats pass; the wet street reflects neon and electric signs.
    - Character motion: Soapy shifts weight from foot to foot, faces the entrance with renewed resolve.
    - Camera directions: Medium shot with Soapy in the foreground, then a slow push-in to the entrance; track a few passing pedestrians to emphasize the bustling, affluent street.
    - Dynamic scene elements: Wet pavement reflections, golden interior light, city nightlife energy.
    - No background music.
    - Finish the sentence within the time frame.
    """
    make_one(image_path=image_path, prompt=prompt)

