from openai import OpenAI
import sys
import time
from helper_functions import image_operations
from datetime import datetime
import re
import os
import glob
from pathlib import Path

with open("api_key.txt", "r") as file:
    api_key = file.read()
client = OpenAI(api_key = api_key)

def make_one(image_path, prompt, output_folder="./intermediate_files/clips"):
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

def voice_maker(voice_folder="./intermediate_files/clips"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    speech_file_path = f"{voice_folder}/speech_{timestamp}.mp4"

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="cedar",
        input="在下倒有一个主意，不知可以行得行不得？",
        instructions="Ancient Chinese poem tone",
    ) as response:
        response.stream_to_file(speech_file_path)


# Run file to use the function one time.
if __name__ == "__main__":
    image_path = "./intermediate_files/images/scene_c5.png"
    # output_folder = "./intermediate_files/clips"

    # prompt="""Fanjin, Male, 40 years old, ancient Chinese style, dressed shabby, standing in a crowded room, reading a Paper, being very suprised and happy.
    # There are many people looking at him, and Fanjin is cheering like 我中了!我中了!
    # """
    # prompt="""Fanjin, Male, 40 years old, ancient Chinese style, dressed shabby. He is on the ground without consciousness. Everyone slowly gathered around. People are saying, 哎呀，这可如何是好啊
    # """
    # prompt="Fanjin's old mother in a room, crying: 怎有这样苦命的事，中了举人，就得了这个怪病，这可如何是好啊. (sigh). Many people were around her, trying to comfort her."
    # make_one(image_path=image_path, prompt=prompt)
    voice_maker()

