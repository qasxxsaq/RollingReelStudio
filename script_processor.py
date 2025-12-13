from openai import OpenAI
import re

with open("api_key.txt", "r") as file:
    api_key = file.read()
client = OpenAI(api_key = api_key)


example = f"""In each scene, produce positive and negative prompts for image generation models. For example:
Scene 1: A Man picked up his hat, smiled and left.
positive: \"SnowWhite, black hair, brown eyes,blue dress, puffy short sleeves, yellow skirt, best quality,\", \"in city street,\"
negative: \"bad quality, blurry, low resolution, ugly, distortions,\"
Use only Man and Women for character names.
"""

def processor(story, num_scenes):
    prompt = f"Turn the below story into a storyboard-oriented script, containing {num_scenes} scenes. In exactly this format, Scene 1, Scene 2, etc.\n"

    full_prompt = f"{prompt}{example}{story}"
    print(f"{prompt}{example}")

    response = client.responses.create(
        model="gpt-5-nano",
        input=full_prompt,
    )

    return response.output_text

def parse(script):
    shots = re.split(r'\n(?=Scene \d+)', script)
    shots = [s.strip() for s in shots if s.strip()]
    
    # Uncomment to exam the parse for debugging purpose
    for s in shots:
        print(s[:100] + "...")

    return shots

# Run this file for an example.
story_file = "./stories/The Gift of the Magi.txt"
with open(story_file, "r", encoding="utf-8") as file:
        story = file.read()
script = processor(story, 15)

script_path = "./intermediate_files/script/script_PNPrompts.txt"
with open(script_path, "w") as file:
    file.write(script)

