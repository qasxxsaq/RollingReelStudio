import sys

# Import the three modules
try:
    # Assuming the three files are in the same directory
    import ChatGPT_script as llm
    import text_treatment as text
    import image_generate_multiple as img
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all three files are in the same directory.")
    sys.exit(1)

def main():
    print("Starting AI Images Generation Pipeline...")
    llm.LLM_main()
    img.img_main()

if __name__ == "__main__":
    main()