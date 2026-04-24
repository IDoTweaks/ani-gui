import sqlite3

def init_db():
    """Creates the database and history table if it doesn't exist."""
    conn = sqlite3.connect("anigui.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            title TEXT PRIMARY KEY,
            image_url TEXT,
            season TEXT,
            last_episode INTEGER
        )
    """)
    conn.commit()
    conn.close()

def update_history(title, image_url, season, episode):
    """Saves or updates a watched episode."""
    conn = sqlite3.connect("anigui.db")
    cursor = conn.cursor()
    # Insert new show, or update the episode if the show already exists
    cursor.execute("""
        INSERT INTO history (title, image_url, season, last_episode)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(title) DO UPDATE SET
            season=excluded.season,
            last_episode=excluded.last_episode
    """, (title, image_url, season, episode))
    conn.commit()
    conn.close()

def get_history():
    """Fetches all watched shows for the Continue tab."""
    conn = sqlite3.connect("anigui.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, image_url, season, last_episode FROM history")
    rows = cursor.fetchall()
    conn.close()
    
    # Return as a list of dictionaries so it plays nicely with our AnimeCard
    return [{"title": r[0], "image_url": r[1], "season": r[2], "episode": r[3]} for r in rows]