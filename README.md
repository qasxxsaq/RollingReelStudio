# RollingReel  
## Introduction
This is an AI-driven tool that can transform written stories into a coherent short film.
This system will interpret a story text, generate corresponding video shots with style and character consistency, and assemble these shots into a final film.

## Instructions for Use
1. Save your story file in ./stories/story.txt
2. Go to main.py, and click run.
3. Done! Enjoy your film.

## Image Generation System Setup Guide  

1. Clone ComfyUI Repository  
git clone https://github.com/comfyanonymous/ComfyUI.git  
cd ComfyUI  

2. Install Dependencies  
Choose the appropriate command based on your hardware:  
For NVIDIA GPU (CUDA 12.1):  
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121  
pip install -r requirements.txt  
For CPU-only systems:  
pip install torch torchvision torchaudio  
pip install -r requirements.txt  

3. Set Up Project Structure  
Place the files in the following directory structure:  
your-project/  
├── ComfyUI/  
├── ChatGPT_script.py  
├── text_treatment.py  
├── image_generate_multiple.py  
├── scene_generator.py  
├── stories/  
│   └── story.txt  
├── intermediate_files/  
│   ├── images/  
│   └── scripts/  
└── prompt_SG.txt  

4. Download and Place Models  
Diffusion Models (Checkpoints):  
Download your preferred diffusion model (e.g., Flux)  
Place it in: /ComfyUI/models/checkpoints/  
LoRA Models:  
Download your LoRA models  
Place them in: /ComfyUI/models/loras/  

5. Configure Model Names  
Open image_generate_multiple.py and update the model names in the ing_main() function.  
def img_main():  
    checkpoint_name = "flux1-schnell.safetensors"  # Change to your checkpoint filename  
    lora_name = "your-lora-model.safetensors"      # Change to your LoRA filename  
    
6. Configure API Key  
Open ChatGPT_script.py and update the API key in the LLM_main() function:  
API_KEY = "your-actual-api-key-here"  

7. Start ComfyUI Server  
cd ComfyUI  
python main.py --port 8188  

8. Run the Scene Generator:  
cd your-project  
put your story in stories/story.txt  
python scene_generator.py  
python script_processor_for_video.py  
python clip_maker_sora.py  
python film_editor.py  
Alternatively:  
python main.py  

10. Output  
In /intermediate_files, you can find /images, /scripts and /films.  
Final product is in /films  


