Voice Transcriber App
=====================

A Python-based desktop application for real-time speech transcription with voice command support. 
The app listens to your microphone, transcribes spoken words, and allows voice-controlled file management.

Features
--------

- Real-time transcription of speech into text.
- Voice commands for controlling the app:
  * start transcriber      → Begin writing
  * pause transcriber      → Pause transcription
  * stop transcriber       → Stop transcription
  * resume transcriber     → Resume transcription
  * save the file          → Save transcript with default name
  * save the file as <name>→ Save transcript with a custom name
  * delete last line       → Remove the last line of text
  * start all over / clear all → Clear all text
  * show folders           → Open the folder containing transcripts
  * toggle noise           → Enable or disable noise reduction
  * enable voice feedback / disable voice feedback
  * close transcriber      → Close the application
- Automatic file naming with timestamps.
- Voice feedback after every command.
- GUI panels for Listening, Writing/Transcription, Commands, and System Logs.
- Saves transcripts as `.docx` files by default.
- Adjustable noise reduction and visual feedback.

Installation
------------

1. Ensure Python 3.8+ is installed on your system.
2. Install required Python packages:
   pip install pyaudio SpeechRecognition python-docx
3. Run the app:
   python main.py

Optional: You can create a standalone EXE using PyInstaller:

   pyinstaller --onefile --windowed --icon=assets/app_icon.ico main.py

Usage
-----

1. Launch the app (python main.py or the EXE if created).
2. Speak into your microphone.
3. Use voice commands to control recording, save files, or manage the transcript.
4. Transcripts are saved automatically in the transcriptions/ folder.

Notes
-----

- Voice feedback is enabled by default.
- Ensure your microphone is properly connected and accessible.
- Noise reduction may affect transcription speed and accuracy.
- You can toggle voice feedback with voice commands or manually in the app.

License
-------

MIT License
