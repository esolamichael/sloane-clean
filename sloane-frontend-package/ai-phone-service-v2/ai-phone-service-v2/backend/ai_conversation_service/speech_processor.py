"""
Speech recognition module using Google Cloud Speech API.
"""
import os
import io
from google.cloud import speech
from google.cloud.speech import RecognitionConfig, RecognitionAudio
from google.cloud import texttospeech

class SpeechProcessor:
    """
    Handles speech recognition and text-to-speech conversion using Google Cloud APIs.
    """
    
    def __init__(self):
        """Initialize the speech client and text-to-speech client."""
        self.speech_client = speech.SpeechClient()
        self.tts_client = texttospeech.TextToSpeechClient()
    
    def recognize_speech(self, audio_content, language_code="en-US"):
        """
        Convert speech to text using Google Cloud Speech API.
        
        Args:
            audio_content (bytes): The audio content to recognize.
            language_code (str): The language code for recognition.
            
        Returns:
            str: The recognized text.
        """
        audio = RecognitionAudio(content=audio_content)
        config = RecognitionConfig(
            encoding=RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
            model="phone_call",  # Optimized for phone calls
        )
        
        response = self.speech_client.recognize(config=config, audio=audio)
        
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript
        
        return transcript
    
    def text_to_speech(self, text, language_code="en-US", voice_name="en-US-Wavenet-F"):
        """
        Convert text to speech using Google Cloud Text-to-Speech API.
        
        Args:
            text (str): The text to convert to speech.
            language_code (str): The language code for the voice.
            voice_name (str): The name of the voice to use.
            
        Returns:
            bytes: The audio content.
        """
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.95,  # Slightly slower for better clarity
            pitch=0.0,  # Default pitch
            sample_rate_hertz=16000,
        )
        
        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        return response.audio_content
