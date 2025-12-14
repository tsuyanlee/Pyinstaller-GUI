# Voice Transcriber App

A Python-based voice transcription tool with real-time speech recognition, voice commands, and automatic file saving. Built with Tkinter for GUI and Pyaudio/SpeechRecognition for audio input.

## Features

- Real-time transcription of spoken words into text.
- Voice commands:
  - `start transcriber` → start writing
  - `pause transcriber` → pause writing
  - `stop transcriber` → stop writing
  - `resume transcriber` → resume writing
  - `save the file` → save transcription with default name
  - `save the file as <name>` → save with custom file name
  - `delete last line` → remove previous line
  - `start all over` / `clear all` → clear transcript
  - `show folders` → open folder with transcripts
  - `toggle noise` → toggle noise reduction
  - `enable voice feedback` / `disable voice feedback`
  - `close transcriber` → close the app
- Automatic file naming with timestamps.
- Voice feedback after each command.
- Adjustable noise reduction and VU meter visualization.
- Save transcripts as `.docx` files.
- GUI with separate panels for Listening, Transcription, Commands, and System Logs.

## Installation

1. Ensure Python 3.8+ is installed.
2. Install required packages:
   ```bash
   pip install pyaudio SpeechRecognition python-docx
3. Run the app:
   python main.py

## Optional: You can create a standalone EXE using PyInstaller:

   pyinstaller --onefile --windowed --icon=assets/app_icon.ico main.py

## Usage

1. Launch the app (python main.py or the EXE if created).
2. Speak into your microphone.
3. Use voice commands to control recording, save files, or manage the transcript.
4. Transcripts are saved automatically in the transcriptions/ folder.

## Notes

- Voice feedback is enabled by default.
- Ensure your microphone is properly connected and accessible.
- Noise reduction may affect transcription speed and accuracy.
- You can toggle voice feedback with voice commands or manually in the app.

## License

MIT license