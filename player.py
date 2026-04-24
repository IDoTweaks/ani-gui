import subprocess

def play_episode(anime_title, episode_number):
    """
    Invisibly launches ani-cli in the background.
    Passes the specific episode number to skip selection screens.
    """
    print(f"Starting ani-cli for {anime_title} Episode {episode_number}...")
    
    try:
        # Popen runs this in the background without freezing PyQt6
        # Example: ani-cli "Bungo Stray Dogs" -e 1
        subprocess.Popen(["ani-cli", anime_title, "-e", str(episode_number)])
    except Exception as e:
        print(f"Failed to launch ani-cli: {e}")
        print("Ensure ani-cli and a video player like mpv are installed on Fedora.")