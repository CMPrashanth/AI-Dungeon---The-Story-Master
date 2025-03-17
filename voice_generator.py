import re
import pyttsx3
import time
import random
import tempfile
import os
from pydub import AudioSegment

class VoiceNarrator:
    """
    This class generates an audio narration file from text that contains modulation
    instructions. The text is split into segments, each rendered separately with the
    appropriate properties, then concatenated into one file. It also returns a mapping
    of segments for text highlighting.
    """
    def __init__(self):
        self.engine = pyttsx3.init()
        self.default_rate = 175
        self.default_volume = 0.8
        self.default_pitch = 100
        self.engine.setProperty('rate', self.default_rate)
        self.engine.setProperty('volume', self.default_volume)
        voices = self.engine.getProperty('voices')
        self.voices = {voice.id: voice for voice in voices}
        if voices:
            self.engine.setProperty('voice', voices[0].id)

    def parse_modulation_instructions(self, text):
        """
        Parses modulation instructions in square brackets and splits the text into segments.
        Returns a list of (plain_text, properties) tuples.
        """
        segments = []
        current_text = ""
        current_properties = {
            'rate': self.default_rate,
            'volume': self.default_volume,
            'pitch': self.default_pitch,
            'pause_before': 0,
            'pause_after': 0
        }
        pattern = r'\[([^\]]+)\]'
        parts = re.split(pattern, text)
        for i, part in enumerate(parts):
            if i % 2 == 0:
                current_text += part
            else:
                instruction = part.strip().upper()
                if instruction in ("SOFT TONE", "SOFT REFLECTIVE TONE"):
                    current_properties['volume'] = 0.7
                    current_properties['rate'] = self.default_rate - 20
                elif instruction == "SLOWER PACE":
                    current_properties['rate'] = self.default_rate - 30
                elif instruction in ("FASTER PACE", "INCREASE PACE"):
                    current_properties['rate'] = self.default_rate + 30
                elif instruction == "ENERGETIC TONE":
                    current_properties['volume'] = 0.9
                    current_properties['pitch'] = 110
                elif instruction in ("INCREASED VOLUME", "INCREASE VOLUME"):
                    current_properties['volume'] = 0.95
                elif instruction == "EMPHASIS":
                    current_properties['pitch'] = 110
                elif instruction in ("BRIEF PAUSE", "PAUSE"):
                    current_properties['pause_after'] = 500  # 500 ms
                elif instruction == "PAUSE BRIEFLY":
                    current_properties['pause_before'] = 300  # 300 ms
                elif instruction == "PAUSE LONGER":
                    current_properties['pause_after'] = 1000  # 1 sec
                elif instruction == "RISING INTONATION":
                    current_properties['pitch'] = 115
                elif instruction == "TENSE TREMBLING TONE":
                    current_properties['rate'] = self.default_rate - 10
                    current_properties['pitch'] = 105
                elif instruction == "BRIGHT UPLIFTED TONE":
                    current_properties['rate'] = self.default_rate + 10
                    current_properties['pitch'] = 110
                    current_properties['volume'] = 0.85
                elif instruction == "SOMBER HEAVY TONE":
                    current_properties['rate'] = self.default_rate - 20
                    current_properties['pitch'] = 90
                    current_properties['volume'] = 0.75
                elif instruction == "SHARP INTENSE TONE":
                    current_properties['rate'] = self.default_rate + 15
                    current_properties['pitch'] = 105
                    current_properties['volume'] = 0.9
                elif instruction in ("DIALOGUE VOICE", "CONVERSATIONAL TONE"):
                    current_properties['pitch'] = 105
                    current_properties['rate'] = self.default_rate + 5
                elif instruction == "EMOTIVE":
                    current_properties['volume'] = min(current_properties['volume'] + 0.1, 1.0)
                    current_properties['pitch'] += 5
                elif instruction == "NATURAL":
                    current_properties['rate'] = self.default_rate
                elif instruction == "THRILLING":
                    current_properties['volume'] = 0.95
                    current_properties['pitch'] += 10
                elif instruction in ("SCENE CHANGE", "SHIFT TONE"):
                    if current_text:
                        # Append current segment
                        segments.append((current_text.strip(), dict(current_properties)))
                        current_text = ""
                    # Reset properties for new segment with a pause before
                    current_properties = {
                        'rate': self.default_rate,
                        'volume': self.default_volume,
                        'pitch': self.default_pitch,
                        'pause_before': 1000,
                        'pause_after': 0
                    }
        if current_text:
            segments.append((current_text.strip(), dict(current_properties)))
        return segments

    def save_to_temp_file(self, text):
        """
        Saves the narrated audio (with modulation cues applied) to a temporary WAV file.
        Returns a tuple (final_file, mapping) where mapping is a list of dictionaries,
        each containing 'text', 'start_time', and 'end_time' in milliseconds.
        """
        segments = self.parse_modulation_instructions(text)
        segment_files = []
        mapping = []
        current_time = 0
        temp_dir = tempfile.mkdtemp()
        for i, (segment_text, properties) in enumerate(segments):
            seg_file = os.path.join(temp_dir, f"segment_{i}.wav")
            self.engine.setProperty('rate', properties['rate'])
            self.engine.setProperty('volume', properties['volume'])
            try:
                self.engine.setProperty('pitch', properties['pitch'])
            except Exception:
                pass
            self.engine.save_to_file(segment_text, seg_file)
            self.engine.runAndWait()
            seg_audio = AudioSegment.from_file(seg_file)
            seg_duration = len(seg_audio)  # duration in ms
            mapping.append({
                "text": segment_text,
                "start_time": current_time,
                "end_time": current_time + seg_duration
            })
            current_time += seg_duration
            segment_files.append(seg_file)
            if properties['pause_after'] > 0:
                silence = AudioSegment.silent(duration=properties['pause_after'])
                silence_file = os.path.join(temp_dir, f"silence_{i}.wav")
                silence.export(silence_file, format="wav")
                segment_files.append(silence_file)
                current_time += properties['pause_after']
        final_audio = AudioSegment.empty()
        for file in segment_files:
            seg = AudioSegment.from_file(file)
            final_audio += seg
        final_file = os.path.join(temp_dir, "final_narration.wav")
        final_audio.export(final_file, format="wav")
        return final_file, mapping

if __name__ == "__main__":
    # For testing purposes.
    narrator = VoiceNarrator()
    test_text = (
        "[SOFT REFLECTIVE TONE] The old castle stood silently on the hill, its ancient stones gleaming in the moonlight. "
        "[CONVERSATIONAL TONE] Alice approached the heavy wooden door. \"Is anyone there?\" she called out nervously. "
        "[FASTER PACE] [ENERGETIC TONE] Suddenly, a crash echoed through the hallway! Something was moving quickly in the darkness. "
        "[INCREASED VOLUME] \"Who goes there?\" demanded a deep voice from within. "
        "[THRILLING] [TENSE TREMBLING TONE] Alice's heart raced as she contemplated her next move."
    )
    audio_file, mapping = narrator.save_to_temp_file(test_text)
    print("Audio file saved at:", audio_file)
    print("Mapping:", mapping)
