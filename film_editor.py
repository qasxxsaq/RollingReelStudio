from moviepy.editor import VideoFileClip, concatenate_videoclips, afx
import os
import glob
import re
from datetime import datetime

# Sort in the way that "file10" is after "file1".
def numerical_sort(value):
    numbers = re.findall(r'\d+', os.path.basename(value))
    return int(numbers[0]) if numbers else 0

def edit(clip_folder="./intermediate_files/clips", output_folder="films", num_videos=None):

    # Parameter checks
    if not os.path.exists(clip_folder):
        print(f"Folder '{clip_folder}' does not exist!")
        return None

    # Sort videos and concatenate to make the film
    video_files = sorted(glob.glob(os.path.join(clip_folder, "*.mp4")), key=numerical_sort)
    if not video_files:
        raise FileNotFoundError(f"No mp4 videos found in '{clip_folder}'")

    if num_videos is not None:
        video_files = video_files[:num_videos]

    clips = []
    for v in video_files:
        clip = VideoFileClip(v)
        # Add audio fades
        clip = clip.fx(afx.audio_fadein, 0.2)
        clip = clip.fx(afx.audio_fadeout, 0.2)
        clips.append(clip)
    film = concatenate_videoclips(clips, method="compose")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if output_folder is not None:
        os.makedirs(output_folder, exist_ok=True)
        output_path = f"./{output_folder}/film_{timestamp}.mp4"
    else:
        output_path = f"film_{timestamp}.mp4"

    film.write_videofile(output_path, codec="libx264")

# Run for testing.
if __name__ == "__main__":
    clip_folder = "./intermediate_files/clips"
    output_folder = "films"
    edit(clip_folder, output_folder)

