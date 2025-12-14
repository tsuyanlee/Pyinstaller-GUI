# installer_gui.py

"""
PyInstaller Builder (Tkinter) - extended with Conda env dropdown & better env terminal support.
Added: Multi-file/folder selection for copying to EXE folder.
"""

import os
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ---------- Utility helpers ----------
def quote_path(p: str) -> str:
    if not p:
        return p
    if "\"" in p:
        return p
    if " " in p or "(" in p or ")" in p:
        return f'"{p}"'
    return p

def find_python_in_venv(project_folder: str):
    candidates = [".venv", "venv", "env", ".env"]
    for c in candidates:
        base = os.path.join(project_folder, c)
        if os.path.isdir(base):
            py_win = os.path.join(base, "Scripts", "python.exe")
            py_unix = os.path.join(base, "bin", "python")
            if os.path.isfile(py_win):
                return py_win
            if os.path.isfile(py_unix):
                return py_unix
    py_win = os.path.join(project_folder, "Scripts", "python.exe")
    py_unix = os.path.join(project_folder, "bin", "python")
    if os.path.isfile(py_win):
        return py_win
    if os.path.isfile(py_unix):
        return py_unix
    return None

def parse_conda_envs_from_output(output: str):
    envs = []
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        last = parts[-1]
        if os.path.isabs(last) or (":" in last) or ("\\" in last) or ("/" in last):
            path = last
            name = parts[0].lstrip("*")
            envs.append((name, path))
    return envs

# ---------- Main GUI ----------
class PyInstallerBuilder:
    def __init__(self, master):
        self.master = master
        master.title("PyInstaller Builder")
        master.geometry("1000x700")
        master.minsize(900, 650)

        # Variables
        self.project_folder = tk.StringVar()
        self.main_script = tk.StringVar()
        self.icon_file = tk.StringVar()
        self.python_exe = tk.StringVar()
        self.onefile_var = tk.BooleanVar(value=True)
        self.windowed_var = tk.BooleanVar(value=True)
        self.clean_build_var = tk.BooleanVar(value=False)

        # Add-data entries: list of strings
        self.adddata_entries = []

        # Conda env list store
        self.conda_envs = []  # list of (name, path)
        self.conda_env_var = tk.StringVar()

        # ---------- Top frame ----------
        frame_top = tk.Frame(master)
        frame_top.pack(fill=tk.X, padx=12, pady=10)

        # Project folder
        tk.Label(frame_top, text="Project Folder:", anchor="w").grid(row=0, column=0, sticky="w", pady=2)
        tk.Entry(frame_top, textvariable=self.project_folder, width=90).grid(row=0, column=1, padx=6, pady=2)
        tk.Button(frame_top, text="Browse", command=self.browse_folder).grid(row=0, column=2, padx=2, pady=2)

        # Main script
        tk.Label(frame_top, text="Main Script (.py):", anchor="w").grid(row=1, column=0, sticky="w", pady=2)
        tk.Entry(frame_top, textvariable=self.main_script, width=90).grid(row=1, column=1, padx=6, pady=2)
        tk.Button(frame_top, text="Browse", command=self.browse_script).grid(row=1, column=2, padx=2, pady=2)

        # Icon
        tk.Label(frame_top, text="Icon (.ico, optional):", anchor="w").grid(row=2, column=0, sticky="w", pady=2)
        tk.Entry(frame_top, textvariable=self.icon_file, width=90).grid(row=2, column=1, padx=6, pady=2)
        tk.Button(frame_top, text="Browse", command=self.browse_icon).grid(row=2, column=2, padx=2, pady=2)

        # Python exe
        tk.Label(frame_top, text="Project Python (python.exe):", anchor="w").grid(row=3, column=0, sticky="w", pady=(8,2))
        tk.Entry(frame_top, textvariable=self.python_exe, width=90).grid(row=4, column=0, columnspan=3, padx=6, pady=(2,4), sticky="we")

        btn_frame = tk.Frame(frame_top)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=(0, 8))
        tk.Button(btn_frame, text="Select", command=self.browse_python).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Auto-detect venv", command=self.autodetect_venv).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Open Env Terminal", command=self.open_env_terminal).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="System Python", command=self.use_system_python).pack(side=tk.LEFT, padx=6)

        # Conda env
        tk.Label(frame_top, text="Conda Environment:", anchor="w").grid(row=6, column=0, sticky="w", pady=(4,2))
        self.conda_env_menu = ttk.Combobox(frame_top, textvariable=self.conda_env_var, width=88, state="readonly")
        self.conda_env_menu.bind("<<ComboboxSelected>>", self.on_conda_env_selected)
        self.conda_env_menu.grid(row=6, column=1, padx=6, pady=(4,2), sticky="we")
        tk.Button(frame_top, text="Refresh Conda Envs", command=self.load_conda_envs).grid(row=6, column=2, padx=6, pady=(4,2))

        # ---------- Add-data UI ----------
        adddata_frame = tk.Frame(master)
        adddata_frame.pack(fill=tk.X, padx=12, pady=(8,0))
        tk.Label(adddata_frame, text="Add data entries (files/folders to include in EXE):").pack(anchor="w")

        ad_input_frame = tk.Frame(adddata_frame)
        ad_input_frame.pack(fill=tk.X, pady=(4,6))
        tk.Button(ad_input_frame, text="Browse Files", command=self.browse_adddata_files).pack(side=tk.LEFT, padx=(0,6))
        tk.Button(ad_input_frame, text="Browse Folder", command=self.browse_adddata_folder).pack(side=tk.LEFT, padx=(0,6))
        tk.Button(ad_input_frame, text="Remove Selected", command=self.remove_selected_adddata).pack(side=tk.LEFT, padx=(6,0))

        self.adddata_listbox = tk.Listbox(adddata_frame, height=4)
        self.adddata_listbox.pack(fill=tk.X, padx=6)

        # Options
        options_frame = tk.Frame(master)
        options_frame.pack(fill=tk.X, padx=12, pady=(8,4))
        tk.Checkbutton(options_frame, text="--onefile", variable=self.onefile_var).pack(side=tk.LEFT, padx=6)
        tk.Checkbutton(options_frame, text="--windowed (no console)", variable=self.windowed_var).pack(side=tk.LEFT, padx=6)
        tk.Checkbutton(options_frame, text="Clean build (delete build/ and dist/ before building)", variable=self.clean_build_var).pack(side=tk.LEFT, padx=12)

        # Build button & progress
        action_frame = tk.Frame(master)
        action_frame.pack(fill=tk.X, padx=12, pady=8)
        self.build_button = tk.Button(action_frame, text="Build EXE", bg="#2e8b57", fg="white", command=self.start_build)
        self.build_button.pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(action_frame, mode="indeterminate", length=400)
        self.progress.pack(side=tk.LEFT, padx=12)

        # Log area
        tk.Label(master, text="Output Log:").pack(anchor="w", padx=12)
        self.log_box = tk.Text(master, height=18, wrap="none")
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,12))
        xscroll = tk.Scrollbar(master, orient=tk.HORIZONTAL, command=self.log_box.xview)
        xscroll.pack(fill=tk.X, padx=12)
        self.log_box.configure(xscrollcommand=xscroll.set)

        # Status bar
        self.status_var = tk.StringVar(value="Idle")
        tk.Label(master, textvariable=self.status_var, anchor="w").pack(fill=tk.X, padx=12, pady=(0,8))

        # Load conda envs
        self.load_conda_envs()

    # ---------- Browse callbacks ----------
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.project_folder.set(folder)
            if not self.main_script.get():
                for f in os.listdir(folder):
                    if f.endswith(".py") and f.lower().startswith("main"):
                        self.main_script.set(os.path.join(folder, f))
                        break

    def browse_script(self):
        f = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if f:
            self.main_script.set(f)

    def browse_icon(self):
        f = filedialog.askopenfilename(filetypes=[("ICO Files", "*.ico")])
        if f:
            self.icon_file.set(f)

    def browse_python(self):
        f = filedialog.askopenfilename(filetypes=[("Python Executable", "python.exe")])
        if f:
            self.python_exe.set(f)

    def autodetect_venv(self):
        folder = self.project_folder.get()
        if not folder:
            messagebox.showinfo("Auto-detect", "Select the project folder first.")
            return
        py = find_python_in_venv(folder)
        if py:
            self.python_exe.set(py)
            messagebox.showinfo("Auto-detect", f"Found python at:\n{py}")
        else:
            messagebox.showinfo("Auto-detect", "No virtualenv found inside project folder.")

    # ---------- Conda ----------
    def load_conda_envs(self):
        try:
            result = subprocess.run("conda env list", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.conda_envs = []
                self.conda_env_menu["values"] = []
                self.log("conda not available or returned error when listing envs.")
                return
            envs = parse_conda_envs_from_output(result.stdout)
            self.conda_envs = envs
            self.conda_env_menu["values"] = [name for name, _ in envs]
            if "base" in [n for n,_ in envs] and not self.conda_env_var.get():
                self.conda_env_var.set("base")
            self.log(f"Detected conda envs: {', '.join([n for n,_ in envs])}")
        except Exception as e:
            self.log(f"Error detecting conda envs: {e}")
            self.conda_envs = []
            self.conda_env_menu["values"] = []

    # ---------- Add-data management ----------
    def browse_adddata_files(self):
        files = filedialog.askopenfilenames(title="Select files to include")
        if not files:
            return
        for f in files:
            dest = os.path.basename(f)
            entry = f"{f};{dest}"
            if entry not in self.adddata_entries:
                self.adddata_entries.append(entry)
                self.adddata_listbox.insert(tk.END, entry)

    def browse_adddata_folder(self):
        folder = filedialog.askdirectory(title="Select a folder to include")
        if not folder:
            return
        dest = os.path.basename(folder)
        entry = f"{folder};{dest}"
        if entry not in self.adddata_entries:
            self.adddata_entries.append(entry)
            self.adddata_listbox.insert(tk.END, entry)

    def remove_selected_adddata(self):
        sel = list(self.adddata_listbox.curselection())
        if not sel:
            return
        for i in reversed(sel):
            self.adddata_listbox.delete(i)
            del self.adddata_entries[i]

    # ---------- Logging ----------
    def log(self, msg: str):
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)

    # ---------- Terminal ----------
    def open_env_terminal(self):
        python_path = self.python_exe.get().strip()
        conda_choice = self.conda_env_var.get().strip()
        if python_path and os.path.isfile(python_path):
            env_dir = os.path.dirname(os.path.dirname(python_path))
            activate_bat = os.path.join(env_dir, "Scripts", "activate.bat")
            if os.path.isfile(activate_bat):
                os.system(f'start cmd.exe /K "{activate_bat}"')
                return
        if conda_choice:
            try:
                os.system(f'start cmd.exe /K "conda activate {conda_choice}"')
                return
            except Exception as e:
                self.log(f"Failed to open conda terminal for {conda_choice}: {e}")
        os.system("start cmd")

    # ---------- Build ----------
    def start_build(self):
        folder = self.project_folder.get().strip()
        script = self.main_script.get().strip()
        python_exec = self.python_exe.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid project folder.")
            return
        if not script or not os.path.isfile(script):
            messagebox.showerror("Error", "Please select the main script (.py).")
            return
        if python_exec and not os.path.isfile(python_exec):
            messagebox.showerror("Error", "Selected python.exe path is invalid.")
            return
        if not python_exec:
            if not messagebox.askyesno("Python not selected",
                                       "No python.exe selected for target project.\n"
                                       "Continue with current python?"):
                return
        if self.clean_build_var.get():
            try:
                bpath = os.path.join(folder, "build")
                dpath = os.path.join(folder, "dist")
                if os.path.isdir(bpath):
                    shutil.rmtree(bpath)
                    self.log("Removed build/ folder.")
                if os.path.isdir(dpath):
                    shutil.rmtree(dpath)
                    self.log("Removed dist/ folder.")
            except Exception as e:
                self.log(f"Warning: could not clean build/dist: {e}")
        self.build_button.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_var.set("Building...")
        self.log_box.delete("1.0", tk.END)
        t = threading.Thread(target=self.run_pyinstaller, args=(folder, script, python_exec))
        t.daemon = True
        t.start()

    def run_pyinstaller(self, folder, script, python_exec):
        try:
            cmd_parts = []
            if python_exec:
                cmd_parts.extend([quote_path(python_exec), "-m", "PyInstaller"])
            else:
                cmd_parts.extend(["pyinstaller"])
            if self.onefile_var.get():
                cmd_parts.append("--onefile")
            if self.windowed_var.get():
                cmd_parts.append("--windowed")
            icon = self.icon_file.get().strip()
            if icon:
                cmd_parts.append(f"--icon={quote_path(icon)}")
            cmd_parts.append(quote_path(os.path.abspath(script)))
            full_cmd = " ".join(cmd_parts)
            self.log(f"Running command:\n{full_cmd}")
            process = subprocess.Popen(full_cmd, cwd=folder, shell=True,
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True, bufsize=1)
            for line in iter(process.stdout.readline, ""):
                if line:
                    self.log(line.rstrip())
            process.stdout.close()
            rc = process.wait()
            if rc == 0:
                self.log("Build finished successfully.")
                self.status_var.set("Build completed.")

                # Copy Add-data entries
                dist_folder = os.path.join(folder, "dist")
                exe_name = os.path.splitext(os.path.basename(script))[0]
                exe_folder = os.path.join(dist_folder, exe_name)
                if self.onefile_var.get():
                    exe_folder = dist_folder
                for entry in self.adddata_entries:
                    src = entry.split(";")[0] if ";" in entry else entry
                    src = os.path.abspath(src)
                    if os.path.isfile(src):
                        shutil.copy(src, exe_folder)
                        self.log(f"Copied {src} -> {exe_folder}")
                    elif os.path.isdir(src):
                        dest_folder = os.path.join(exe_folder, os.path.basename(src))
                        shutil.copytree(src, dest_folder, dirs_exist_ok=True)
                        self.log(f"Copied {src} -> {dest_folder}")

                messagebox.showinfo("Success", f"EXE created. Check dist folder:\n{exe_folder}")
            else:
                self.log(f"Build failed with return code: {rc}")
                self.status_var.set("Build failed.")
                messagebox.showerror("Build failed", f"PyInstaller exited with code {rc}.")
        except Exception as e:
            self.log(f"Unexpected error: {e}")
            self.status_var.set("Error")
            messagebox.showerror("Error", str(e))
        finally:
            self.progress.stop()
            self.build_button.config(state=tk.NORMAL)

    # ---------- Conda selection ----------
    def on_conda_env_selected(self, event=None):
        selected = self.conda_env_var.get().strip()
        if not selected:
            return
        for name, path in self.conda_envs:
            if name == selected:
                python_path = os.path.join(path, "python.exe")
                if os.path.isfile(python_path):
                    self.python_exe.set(python_path)
                    self.log(f"Selected Conda env python.exe: {python_path}")
                    self.status_var.set(f"Using Conda environment: {selected}")
                return

    # ---------- System Python ----------
    def use_system_python(self):
        import shutil
        self.conda_env_var.set("")
        self.conda_env_menu["values"] = []
        self.status_var.set("Using system Python")
        p = shutil.which("python")
        if p and os.path.isfile(p):
            self.python_exe.set(p)
            self.log(f"System Python detected: {p}")
            messagebox.showinfo("System Python", f"System Python detected:\n{p}")
            return
        messagebox.showerror("Python Not Found", "Could not find a system Python installation.")
        self.log("System Python not found.")

# ---------- Run app ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = PyInstallerBuilder(root)
    root.mainloop()
