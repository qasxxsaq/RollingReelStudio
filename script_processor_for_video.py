from openai import OpenAI
import re

with open("api_key_openAI_binbin.txt", "r") as file:
    api_key = file.read()
client = OpenAI(api_key = api_key)

def processor(script, story=None, output_path=None):
    prompt1 = "For each scene, summarize into a plot. Describe explicit character motion instructions, camera directions, and dynamic scene elements. Use High-Motion Prompt language for video generation models when appropreate. In this format, Scene 1, Scene 2, etc.\n"
    
    if story is not None:
        prompt2 = "\nThe original story is given below for reference:\n"
        full_prompt = f"{prompt1}{script}{prompt2}{story}"
    else:
         full_prompt = f"{prompt1}{script}"
    # print(full_prompt)

    response = client.responses.create(
        model="gpt-5-nano",
        input=full_prompt,
    )

    if output_path is not None:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(response.output_text)

    return response.output_text

def parse(script):
    shots = re.split(r'\n(?=Scene \d+)', script, flags=re.IGNORECASE)
    shots = [s.strip() for s in shots if s.strip()]
    
    # Uncomment to exam the parse for debugging purpose
    for s in shots:
        print(s[:100] + "...")

    return shots

def main(story_path = "./stories/story.txt",
         script_prompt_path = "./intermediate_files/scripts/script_PNPrompts.txt",
         script_plot_path = "./intermediate_files/scripts/script_plot.txt"):
    
    with open(story_path, "r", encoding="utf-8") as file:
            story = file.read()
    with open(script_prompt_path, "r", encoding="utf-8") as file:
            script_prompt = file.read()

    script_plot = processor(script=script_prompt, story=story, output_path=script_plot_path)
    scenes = parse(script_plot)

    return scenes


## This file can be run individually for one-time operations.
if __name__ == "__main__":

    # processor
    story_path = "./stories/The Cop and the Anthem.txt"
    with open(story_path, "r", encoding="utf-8") as file:
            story = file.read()

    script_prompt_path = "./intermediate_files/scripts/script_PNPrompts_2.txt"
    with open(script_prompt_path, "r", encoding="utf-8") as file:
            script_prompt = file.read()

    script_plot_path = "./intermediate_files/scripts/script_plot_2.txt"

    script_plot = processor(script=script_prompt, story=story, output_path=script_plot_path)

    # parse
    # script_plot_path = "./intermediate_files/scripts/script_plot.txt"
    # with open(script_plot, "r", encoding="utf-8") as file:
    #         script_plot = file.read()
    parse(script_plot)

