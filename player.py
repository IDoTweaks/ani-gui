import subprocess
import os
import stat
import re  # NEW: We need this to clean the text!

def setup_fake_rofi():
    """Creates a fake executable to intercept ani-cli's search results."""
    bin_dir = os.path.abspath("./bin")
    os.makedirs(bin_dir, exist_ok=True)
    rofi_path = os.path.join(bin_dir, "rofi")
    
    script = """#!/bin/bash
cat > /tmp/anigui_seasons.txt
exit 1
"""
    with open(rofi_path, "w") as f:
        f.write(script)
    
    st = os.stat(rofi_path)
    os.chmod(rofi_path, st.st_mode | stat.S_IEXEC)
    return bin_dir

def fetch_ani_cli_seasons(query):
    """Invisibly runs ani-cli, steals the exact season names, and cleans the text."""
    bin_dir = setup_fake_rofi()
    
    if os.path.exists("/tmp/anigui_seasons.txt"):
        os.remove("/tmp/anigui_seasons.txt")
        
    env = os.environ.copy()
    env["PATH"] = bin_dir + os.pathsep + env["PATH"]
    
    subprocess.run(["ani-cli", query, "--rofi"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    seasons = []
    if os.path.exists("/tmp/anigui_seasons.txt"):
        with open("/tmp/anigui_seasons.txt", "r") as f:
            for line in f.readlines():
                raw_text = line.strip()
                if raw_text:
                    # --- NEW: The Cleaning Phase ---
                    # 1. Strip leading list numbers (e.g., "1 " or "12. ")
                    clean_text = re.sub(r'^\d+[\.\s]+', '', raw_text)
                    
                    # 2. Strip trailing episode counts (e.g., " (28 episodes)")
                    clean_text = re.sub(r'\s*\(\d+\s*episodes?\)$', '', clean_text, flags=re.IGNORECASE)
                    
                    seasons.append(clean_text)
            
    return seasons if seasons else [query]

def play_episode(exact_title, episode_number, audio_type="Sub"):
    """Launches ani-cli with the clean title and auto-selects the first match (-S 1)."""
    print(f"Playing {exact_title} Ep {episode_number} ({audio_type})...")
    
    command = ["ani-cli", exact_title, "-S", "1", "-e", str(episode_number)]
    
    if audio_type == "Dub":
        command.append("--dub")
        
    subprocess.Popen(command)