# AI-Dungeon Master - Master of Storytelling
Utilize the best chatbot available to create stories with limitless possibilities, let your creativity run wild, and listen to the stories in a sophisticated narrative format.

AI Dungeon Master is an immersive narrative generator that transforms a simple story premise into a rich, engaging, and dynamic narrative. It leverages advanced text-to-speech modulation techniques to deliver a realistic and thrilling voice narration experience.

## Overview

This project combines creative story generation with advanced voice narration. It uses the Gemini API to generate stories enriched with modulation cues and employs the `pyttsx3` TTS engine to deliver the narration with natural and dynamic voice modulation.

## Features

- **Immersive Story Generation:**  
  Transforms a user-provided premise into a complete story with a clear beginning, middle, and end, along with unexpected twists and vivid descriptions.

- **Advanced Voice Narration:**  
  Utilizes embedded bracketed modulation instructions (e.g., `[SOFT REFLECTIVE TONE]`, `[THRILLING]`, `[CONVERSATIONAL TONE]`) to dynamically adjust voice parameters like rate, volume, and pitch.

- **Dynamic and Natural Delivery:**  
  Introduces slight random variations in narration properties to simulate realistic human speech and maintain a natural, engaging delivery.

## Project Structure

- **main.py:**  
  The entry point of the application. It handles user input, enhances the prompt with voice modulation cues, generates the story, and starts the narration. After narration is complete, the program exits automatically.

- **story_generator.py:**  
  Contains the `enhance_prompt` function that enriches the user’s premise with detailed modulation instructions and the logic for generating a story using the Gemini API.

- **voice_generator.py:**  
  Implements the `VoiceNarrator` class for handling text-to-speech narration using `pyttsx3`. It also includes the `generate_voice` helper function to facilitate voice narration with modulation instructions.

## Installation

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Your `requirements.txt` should include:
   - pyttsx3
   - google-generativeai
   - python-dotenv
   - (Other built-in libraries like re, threading, time, and random are included with Python.)

3. **Set Up Environment Variables:**
   Create an `.env` file in an `assets` folder (as expected by the project) and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

Run the application with:
```bash
python main.py
```
- Enter your story premise or scenario when prompted.
- The system will generate an immersive story enriched with modulation instructions.
- The generated story will be displayed and then narrated using the TTS engine.
- After narration is complete, the program will exit automatically.

## Customization

- **Voice Modulation:**  
  You can modify the modulation instructions in the `parse_modulation_instructions` method within `voice_generator.py` to tailor the narration style further.

- **Story Prompt Enhancement:**  
  Adjust the `enhance_prompt` function in `story_generator.py` to modify how the prompt is enriched with narrative and voice modulation cues.

- **API Configuration:**  
  The current implementation uses Gemini's `gemini-1.5-flash` model. You can change this in `story_generator.py` if you wish to use a different model or provider.

## Troubleshooting

- **TTS Limitations:**  
  Some TTS engines may not support pitch adjustments. Errors related to pitch are caught and ignored, ensuring continuous narration.

- **API Key Issues:**  
  Ensure that the `GEMINI_API_KEY` is correctly set in the `.env` file as required by the project structure.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) for providing text-to-speech functionality.
- [Google Generative AI](https://cloud.google.com/generative-ai) for the story generation API.
- Thanks to all contributors for making this immersive storytelling experience possible.
