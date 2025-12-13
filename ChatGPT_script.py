from openai import OpenAI

def read_text_file(filepath: str) -> str:
    """Read content from a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return ""
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        return ""


def get_chatgpt_response(prompt: str, api_key: str, model: str = "gpt-4") -> str:
    """Get response from ChatGPT API."""
    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a screenwriter."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error getting ChatGPT response: {e}")
        return ""


def write_output_file(content: str, output_file: str):
    """Write content to an output text file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Output successfully written to '{output_file}'")
        return True
    except Exception as e:
        print(f"Error writing to file '{output_file}': {e}")
        return False


def LLM_main():
    # Configuration
    FIRST_FILE = "prompt_SG.txt"  # first file path
    SECOND_FILE = "./stories/story.txt"  # second file path
    OUTPUT_FILE = "./intermediate_files/scripts/script_PNPrompts.txt"  # Output file name
    with open("api_key.txt", "r") as file:
        api_key = file.read()
    API_KEY = api_key
    MODEL = "gpt-4o"  #

    print("📖 Reading input files...")

    # Read both text files
    first_part = read_text_file(FIRST_FILE)
    second_part = read_text_file(SECOND_FILE)

    # Check if files were read successfully
    if not first_part:
        print(f"Failed to read '{FIRST_FILE}'. Exiting.")
        return

    if not second_part:
        print(f"Failed to read '{SECOND_FILE}'. Exiting.")
        return

    # Combine the two parts into a single prompt
    combined_prompt = f"{first_part}\n\n{second_part}"

    print("✅ Files read successfully")
    print(f"📝 Combined prompt length: {len(combined_prompt)} characters")

    # Display preview of the prompt
    print("\n📋 Prompt Preview (first 300 chars):")
    print("-" * 50)
    print(combined_prompt[:300] + "..." if len(combined_prompt) > 300 else combined_prompt)
    print("-" * 50)

    # Check if API key is provided
    if not API_KEY:
        print("\n⚠️  Warning: No API key provided. Please add your OpenAI API key to the code.")
        print("Writing combined prompt to output file instead...")
        write_output_file(combined_prompt, OUTPUT_FILE)
        return

    # Get response from ChatGPT
    print("\n🤖 Getting response from ChatGPT...")
    chatgpt_response = get_chatgpt_response(combined_prompt, API_KEY, MODEL)

    if not chatgpt_response:
        print("Failed to get response from ChatGPT. Writing combined prompt to output file...")
        write_output_file(combined_prompt, OUTPUT_FILE)
        return

    # Write ChatGPT response to output file
    print("✍️ Writing ChatGPT response to output file...")
    write_output_file(chatgpt_response, OUTPUT_FILE)

    # Display preview of the response
    print("\n📋 Response Preview (first 500 chars):")
    print("=" * 50)
    print(chatgpt_response[:500] + "..." if len(chatgpt_response) > 500 else chatgpt_response)
    print("=" * 50)
    print(f"📄 Total response length: {len(chatgpt_response)} characters")

