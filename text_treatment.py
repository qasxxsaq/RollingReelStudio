import re

def parse_prompts_file(filename):
    """
    Parse the script_PNPrompts.txt file and extract positive/negative prompts for each shot.
    Returns structured data that's easy to process for image generation.
    """
    shots = []

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()

        # Normalize content - convert to lowercase for case-insensitive matching
        normalized_content = content.lower()

        # More flexible scene splitting - handle various formats
        scenes = re.split(r'scene\s*\d+\s*:', normalized_content)

        # Also try alternative scene formats
        if len(scenes) <= 1:
            scenes = re.split(r'shot\s*\d+\s*:', normalized_content)

        if len(scenes) <= 1:
            scenes = re.split(r'\n\s*\d+\.?\s*\n', normalized_content)

        # Remove empty first element if exists
        if scenes and not scenes[0].strip():
            scenes = scenes[1:]

        for i, scene_content in enumerate(scenes, 1):
            # More flexible prompt extraction - handle various quote types and whitespace
            positive_match = re.search(r'positive\s*:\s*["\']([^"\']*(?:["\'][^"\']*)*)["\']', scene_content)
            negative_match = re.search(r'negative\s*:\s*["\']([^"\']*(?:["\'][^"\']*)*)["\']', scene_content)

            # If no quotes found, try to capture text until next keyword or end
            if not positive_match:
                positive_match = re.search(
                    r'positive\s*:\s*([^:\n]*(?:\n[^:\n]*)*?)(?=\s*(?:negative|positive|scene|shot|$))', scene_content)
            if not negative_match:
                negative_match = re.search(
                    r'negative\s*:\s*([^:\n]*(?:\n[^:\n]*)*?)(?=\s*(?:positive|negative|scene|shot|$))', scene_content)

            if positive_match and negative_match:
                positive_prompt = positive_match.group(1).strip()
                negative_prompt = negative_match.group(1).strip()

                # Clean up - remove extra quotes and normalize whitespace
                positive_prompt = re.sub(r'["\']\s*["\']', ' ', positive_prompt)
                negative_prompt = re.sub(r'["\']\s*["\']', ' ', negative_prompt)

                # Remove any remaining single quotes at start/end
                positive_prompt = re.sub(r'^["\']|["\']$', '', positive_prompt)
                negative_prompt = re.sub(r'^["\']|["\']$', '', negative_prompt)

                # Normalize whitespace
                positive_prompt = re.sub(r'\s+', ' ', positive_prompt).strip()
                negative_prompt = re.sub(r'\s+', ' ', negative_prompt).strip()

                shots.append({
                    'shot_number': i,
                    'positive': positive_prompt,
                    'negative': negative_prompt
                })

        print(f"✅ Successfully parsed {len(shots)} shots")
        return shots

    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"❌ Error parsing file: {e}")
        return []


def save_treated_prompts(shots, output_filename="treated_promtp.txt"):
    """
    Save the treated list to a text file in a readable format.
    """
    try:
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write("TREATED PROMPTS LIST\n")
            file.write("=" * 50 + "\n\n")

            for shot in shots:
                file.write(f"SHOT {shot['shot_number']}:\n")
                file.write(f"Positive: {shot['positive']}\n")
                file.write(f"Negative: {shot['negative']}\n")
                file.write("-" * 40 + "\n\n")

        print(f"✅ Treated list saved to: {output_filename}")

    except Exception as e:
        print(f"❌ Error saving file: {e}")


def get_shots_list():
    filename = "./intermediate_files/scripts/script_PNPrompts.txt"
    shots = parse_prompts_file(filename)
    save_treated_prompts(shots)

    if shots:
        print("\n📝 Parsed Data Structure:")
        print("=" * 50)
        print(shots)
        # Show the structured data ready for processing
        for shot in shots:
            print(f"\n🎬 Shot {shot['shot_number']}:")
            print(f"   ✅ Positive: {shot['positive'][:80]}...")
            print(f"   ❌ Negative: {shot['negative'][:80]}...")

        print(f"\n🎯 Total shots ready for processing: {len(shots)}")
        print("\n💡 Now you can easily iterate through 'shots' list for image generation:")
        print("   for shot in shots:")
        print("       positive = shot['positive']")
        print("       negative = shot['negative']")
        print("       # Send to ComfyUI")

    else:
        print("❌ No shots were parsed.")

    return shots
