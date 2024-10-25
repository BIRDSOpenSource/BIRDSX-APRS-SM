import tkinter as tk
import subprocess
import os

def run_script():
    # Define the path to the virtual environment and the script
    venv_activate = "/home/birdsx/birdsx/bin/activate"
    script_path = "/home/birdsx/Desktop/ORBTEST_autoDirewolf_autorelay_merged_v1.py"
    
    # Command to run the script within the virtual environment
    command = f"source {venv_activate} && python3 {script_path}"
    
    # Run the command
    subprocess.run(command, shell=True)

# Create the main window
root = tk.Tk()
root.title("Run ORBTEST Script")

# Create and place the button
run_button = tk.Button(root, text="Run Script", command=run_script)
run_button.pack(pady=20)

# Start the GUI event loop
root.mainloop()
