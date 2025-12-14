PyInstaller Builder GUI
======================

A simple Tkinter-based GUI tool to convert Python scripts into standalone Windows executables using PyInstaller.

Features
--------

- Select a project folder and the main Python script.
- Optional: set an icon (.ico) for the EXE.
- Select the Python executable of your project or auto-detect virtual environments (venv/.venv/Conda).
- Optionally open a terminal to activate the environment.
- Add multiple --add-data entries for including extra files/folders.
- Options for:
  * --onefile (single EXE)
  * --windowed (no console)
  * Clean build (delete build/ and dist/ folders before building)
- Live log output while building.
- Progress bar during the build process.

Before Build Checklist
----------------------

1. Make sure all Python dependencies for your project are installed in the selected environment.
2. Ensure the main script is correctly selected and runs without errors.
3. Add any extra files or folders your app needs via Add data entries (format: src;dest).
4. (Optional) Set an icon for the EXE.
5. If using a virtual environment or Conda, click "Open Env Terminal" and activate the environment and install dependencies.

How to Use
----------

1. Launch installer_gui.py
2. Select project folder.
3. Select the main Python script.
4. (Optional) Set an icon for your EXE.
5. Select Python executable:
   - Manually, or
   - Auto-detect virtual environment inside project folder.
6. (Optional) Open terminal to activate environment and install dependencies.
7. Add any extra data files (format: src;dest) if required.
8. Choose options:
   - Onefile / Windowed / Clean build
9. Click "Build EXE".
10. Wait until build finishes; check the dist/ folder inside your project.

Notes
-----

- The EXE will include all libraries installed in the selected Python environment.
- If missing modules occur, ensure the environment has all required packages.
- Use "Open Env Terminal" to install or verify packages before building.

Requirements
------------

- Python 3.x
- Tkinter (usually included in Python standard library)
- PyInstaller installed in the Python environment used for building

License
-------

The MIT License (MIT)
Copyright © 2025 Dev Rigan Koijam

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

