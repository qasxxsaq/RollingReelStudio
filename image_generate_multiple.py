import json
import requests
import time
import os
import uuid
import text_treatment
from urllib.parse import urlencode

class ComfyUI_Client:
    def __init__(self, server_address="127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())

    def get_workflow(self, prompt_text, lora_name=None, lora_strength=1.0,
                     width=512, height=512, steps=20, cfg_scale=7, sampler_name="euler",
                     scheduler="normal", seed=None, negative_prompt="",
                     checkpoint_name="flux_dev.safetensors",shot_number=1):
        """
        Create a workflow with proper node connections and optional LoRA support
        """
        # Seed controls the "randomness" in AI image generation
        # Same seed + same parameters = same image every time
        # No seed = different random image each time
        if seed is None:
            seed = int.from_bytes(os.urandom(2), "big")  # generates 2 random bytes

        workflow = {}  # creates an empty dictionary that will store all the nodes
        node_id = 1  # starts counting nodes from 1

        # NODE 1: Load Checkpoint (Base Model); mark as node 1.
        workflow[str(node_id)] = {  # node id 1
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": checkpoint_name
            }
        }
        checkpoint_node = str(node_id)  # "1"
        node_id += 1

        # If LoRA is specified, add LoRA node
        if lora_name:
            # NODE 2: Load LoRA
            workflow[str(node_id)] = {
                "class_type": "LoraLoader",
                "inputs": {
                    "lora_name": lora_name,
                    "strength_model": lora_strength,
                    "strength_clip": lora_strength,
                    "model": [checkpoint_node, 0],  # Model from checkpoint, Output slot 0: The loaded model
                    "clip": [checkpoint_node, 1]  # CLIP from checkpoint, Output slot 1: The loaded CLIP
                }
            }
            lora_node = str(node_id)  # "2"
            node_id += 1
        else:
            # If no LoRA, use checkpoint node directly
            lora_node = checkpoint_node

        # NODE 3: Positive Prompt Encoding
        workflow[str(node_id)] = {  # 3
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt_text,
                "clip": [lora_node, 1]  # Use CLIP (either from LoRA or checkpoint)
            }
        }
        positive_node = str(node_id)
        node_id += 1

        # NODE 4: Negative Prompt Encoding
        workflow[str(node_id)] = {  # 4
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative_prompt,
                "clip": [lora_node, 1]  # same CLIP
            }
        }
        negative_node = str(node_id)
        node_id += 1

        # NODE 5: Create Empty Latent Image,
        # purpose: Creates a blank canvas in the AI's internal format
        workflow[str(node_id)] = {  # 5
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            }
        }
        latent_node = str(node_id)
        node_id += 1

        # NODE 6: KSampler (Image Generation)
        workflow[str(node_id)] = {  # 6
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,  # Randomness control
                "steps": steps,  # Quality iterations (20-30 typical), More steps = more refinement but slower
                "cfg": cfg_scale,  # (3-10 range), How strictly to follow the prompt (7 = good balance)
                "sampler_name": sampler_name,  # Algorithm type
                "scheduler": scheduler,  # Speed vs quality balance
                "denoise": 1.0,  # How much to transform the image
                "model": [lora_node, 0],  # AI model to use
                "positive": [positive_node, 0],
                "negative": [negative_node, 0],
                "latent_image": [latent_node, 0]  # Canvas to paint on
            }
        }
        sampler_node = str(node_id)
        node_id += 1

        # NODE 7: VAE Decode
        # Purpose: Converts AI's internal representation to visible pixels
        workflow[str(node_id)] = {  # 7
            "class_type": "VAEDecode",
            "inputs": {
                "samples": [sampler_node, 0],
                "vae": [checkpoint_node, 2]  # VAE always from original checkpoint
            }
        }
        decode_node = str(node_id)
        node_id += 1

        # NODE 8: Save Image
        workflow[str(node_id)] = {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": f"scene_{shot_number}",
                "images": [decode_node, 0]
            }
        }

        return workflow

    def queue_prompt(self, prompt):
        """Queue prompt to ComfyUI server"""
        # Sends the workflow to ComfyUI server to start image generation.
        p = {"prompt": prompt, "client_id": self.client_id}  # workflow && clientid
        data = json.dumps(p).encode('utf-8')
        req = requests.post(f"http://{self.server_address}/prompt", data=data)
        return req.json()

    def get_image(self, filename, subfolder, folder_type):
        """Downloads generated image"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urlencode(data)
        response = requests.get(f"http://{self.server_address}/view?{url_values}")  # Download Image
        return response.content

    def get_history(self, prompt_id):
        """Get generation history"""
        response = requests.get(f"http://{self.server_address}/history/{prompt_id}")
        return response.json()

    def generate_image(self, prompt, lora_name=None, lora_strength=1.0, **kwargs):
        """
        Generate image with given parameters

        Args:
            prompt (str): Text prompt for generation
            lora_name (str): Name of LoRA file (without path)
            lora_strength (float): LoRA strength (0.0 to 2.0)
            **kwargs: Additional parameters (width, height, steps, cfg, etc.)
        """
        # queue_prompt -> get_history -> get_image
        try:
            # Create workflow
            workflow = self.get_workflow(prompt, lora_name, lora_strength, **kwargs)

            # Queue prompt
            print("Queuing prompt...")
            result = self.queue_prompt(workflow)
            prompt_id = result['prompt_id']
            print(f"Prompt ID: {prompt_id}")

            # Wait for completion
            print("Generating image...")
            while True:
                history = self.get_history(prompt_id)
                if prompt_id in history and history[prompt_id]['outputs']:
                    break
                time.sleep(1)

            # Get generated image
            output = history[prompt_id]['outputs']
            for node_id in output:
                node_output = output[node_id]
                if 'images' in node_output:
                    image_data = node_output['images'][0]
                    image = self.get_image(
                        image_data['filename'],
                        image_data['subfolder'],
                        image_data['type']
                    )
                    return image

            return None

        except Exception as e:
            print(f"Error generating image: {e}")
            return None


def save_image(image_data, filename=None, output_dir="generated_images"):
    """Save image data to custom directory"""
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    if filename is None:
        filename = f"generated_{int(time.time())}.png"

    # Ensure filename is in the custom directory
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image_data)

    print(f"Image saved as: {filepath}")
    return filepath

def read_trigger_positive_or_negative(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None


def img_main():
    # Initialize client
    client = ComfyUI_Client("127.0.0.1:8188")

    # Get shots list from text_treatment
    shots_list = text_treatment.get_shots_list()  # Assuming this function exists in text_treatment
    trigger_positive = read_trigger_positive_or_negative("positive_prompt.txt")
    negative = read_trigger_positive_or_negative("negative_prompt.txt")
    # If the shots list is stored as a variable in text_treatment, you might need:
    # shots_list = text_treatment.shots_list

    print(f"Found {len(shots_list)} shots to generate")

    # Loop through each shot and generate image
    for shot in shots_list:
        shot_number = shot['shot_number']
        trigger_positive = ""
        positive_prompt = trigger_positive+shot['positive']
        negative_prompt = shot['negative']

        print(f"\n--- Generating image for shot {shot_number} ---")
        print(f"Positive prompt: {positive_prompt[:100]}...")
        print(f"Negative prompt: {negative_prompt[:100]}...")

        # Generate image for this shot
        image_data = client.generate_image(
            prompt=positive_prompt,
            negative_prompt=negative_prompt,
            checkpoint_name="flux_dev.safetensors",
            lora_name="[FLUX LoRa] Kalin _Style_v1.0.safetensors",  # You can make this configurable per shot if needed
            lora_strength=1.0,
            width=640,
            height=360,
            steps=20,
            cfg_scale=3.5,
            seed=123 + shot_number,  # Different seed for each shot but predictable
            shot_number=shot_number  # Pass shot number for filename
        )

        if image_data:
            filename = f"scene_{shot_number}.png"  # Format as shot_001.png, shot_002.png, etc.
            save_image(image_data, filename, "./intermediate_files/images")
            print(f"✅ Successfully generated shot {shot_number}")
        else:
            print(f"❌ Failed to generate shot {shot_number}")

        # Optional: Add a small delay between generations to avoid overwhelming the server
        time.sleep(2)

    print(f"\n🎉 Finished generating all {len(shots_list)} shots!")


