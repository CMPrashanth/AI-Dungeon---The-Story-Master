import os
import google.generativeai as genai
import re
import time
from dotenv import load_dotenv 

def load_api_key():
    """Load the Gemini API key from the ../assets/.env file."""
    env_path = os.path.join(os.path.dirname(__file__), "..", "assets", ".env")
    load_dotenv(env_path)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Error: GEMINI_API_KEY is missing from the .env file.")
    return api_key

def enhance_prompt(user_premise):
    """Enhance the user's premise with additional creative instructions and voice modulation cues."""
    enhanced_prompt = f"""
Create an engaging and original short story based on the following premise. 
While generating the story, insert clear bracketed instructions for voice modulation at appropriate moments. 
These instructions should be in square brackets and will guide the narration. For example:

- For calm, reflective scenes or settings, insert [SOFT REFLECTIVE TONE] or [SLOWER PACE].
- For dialogue or conversational moments, insert [CONVERSATIONAL TONE] or [DIALOGUE VOICE].
- For action sequences or dramatic moments, include cues like [FASTER PACE], [ENERGETIC TONE], or [INCREASED VOLUME].
- For emotionally intense or moving moments, insert [EMOTIVE].
- For natural, realistic dialogue and narrative flow, include [NATURAL].
- For climactic, suspenseful, or high-stakes sequences, add [THRILLING].
- For moments of suspense or surprise, also consider adding [TENSE TREMBLING TONE] or [PAUSE LONGER].
- Include [PAUSE] directives where natural breaks would occur.

Premise:
"{user_premise}"

The final story should have a clear beginning, middle, and end; vivid descriptions of the setting and atmosphere; well-developed characters; meaningful dialogue; and an unexpected twist. 
The story should be approximately 500-800 words and include these bracketed modulation instructions naturally throughout the narrative.
"""
    return enhanced_prompt


def generate_text(prompt):
    """Generate a story using the Gemini API."""
    api_key = load_api_key()
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating text: {e}"

def parse_story(story):
    """
    Parses the generated story using [PARAGRAPH] markers instead of newlines.
    Extracts text and any embedded voice cues.
    """
    paragraphs = story.split("[PARAGRAPH]")  # Split based on the special marker
    parsed_paragraphs = []

    for paragraph in paragraphs:
        # Extract voice tone if present
        match = re.search(r'\[(TONE:.*?)\]', paragraph)
        tone = match.group(1) if match else "Default"
        
        # Clean the paragraph by removing voice tone markers
        clean_text = re.sub(r'\[(TONE:.*?)\]', '', paragraph).strip()
        parsed_paragraphs.append((clean_text, tone))

    return parsed_paragraphs

def narrate_story(story):
    """
    Narrates the story in batches, processing one paragraph at a time.
    """
    parsed_story = parse_story(story)

    for text, tone in parsed_story:
        print(f"\nNarrating: {text} (Tone: {tone})")
        generate_voice(text, tone)  # Use voice synthesis with tone adjustments
        time.sleep(1)  # Short delay between sections


