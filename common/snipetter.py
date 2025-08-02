import pyperclip
import subprocess
import time

prev_text = ""
while True:
    text = pyperclip.paste()
    if text != prev_text and "def " in text:
        with open("snippet.py", "w") as f:
            f.write(text)
        print("Running new snippet...")
        print(subprocess.getoutput("python snippet.py"))
        prev_text = text
    time.sleep(2)