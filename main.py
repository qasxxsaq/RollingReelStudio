import scene_generator as sg
import script_processor_for_video as spv
import clip_maker_sora as clm
import film_editor as fe
import re
import os

# Sort in the way that "file10" is after "file1".
def numerical_sort(value):
    numbers = re.findall(r'\d+', os.path.basename(value))
    return int(numbers[0]) if numbers else 0

def rollingreel():
    sg.main() # Scene Generator - prompt oriented script 
    scenes = spv.main() # Script Processor - plot oriented script
    clm.make_many(scenes) # Clip Maker loop
    fe.edit() # Film Editor 

if __name__ == "__main__":
    rollingreel()

