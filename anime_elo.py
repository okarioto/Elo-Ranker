import random
import sqlite3
import os

# --- Elo math ---
def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_rating(rating_a, rating_b, score_a, k=32):
    ea = expected_score(rating_a, rating_b)
    eb = expected_score(rating_b, rating_a)
    rating_a += k * (score_a - ea)
    rating_b += k * ((1 - score_a) - eb)
    return round(rating_a, 2), round(rating_b, 2)

# --- SQLite Elo Tracker ---
class AnimeEloDB:
    def __init__(self, k=32):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "animes.db")

        self.k = k
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS animes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            rating REAL NOT NULL DEFAULT 1500, 
            link TEXT
        )
        """)
        self.conn.commit()

    def add_anime(self, anime, link=None):
        self.cursor.execute("INSERT OR IGNORE INTO animes (name, link) VALUES (?, ?)", (anime,link))
        self.conn.commit()

    def get_rating(self, anime):
        self.cursor.execute("SELECT rating FROM animes WHERE name=?", (anime,))
        result = self.cursor.fetchone()
        return result[0] if result else 1500

    def update_rating(self, anime, rating):
        self.cursor.execute("UPDATE animes SET rating=? WHERE name=?", (rating, anime))
        self.conn.commit()
    
    def edit_anime(self, current_name, new_name=None, new_link=None):
        updates = []
        params = []
        if new_name is not None:
            updates.append("name=?")
            params.append(new_name)
        if new_link is not None:
            updates.append("link=?")
            params.append(new_link)
        if not updates:
            return  # Nothing to update
        params.append(current_name)
        sql = f"UPDATE animes SET {', '.join(updates)} WHERE name=?"
        self.cursor.execute(sql, tuple(params))
        self.conn.commit()

    def delete_anime(self, name):
        self.cursor.execute("DELETE FROM animes WHERE name=?", (name,))
        self.conn.commit()

    def match(self, anime_a, anime_b, winner):
        self.add_anime(anime_a)
        self.add_anime(anime_b)

        rating_a = self.get_rating(anime_a)
        rating_b = self.get_rating(anime_b)

        if winner == anime_a:
            score_a = 1
        elif winner == anime_b:
            score_a = 0
        else:
            score_a = 0.5

        new_a, new_b = update_rating(rating_a, rating_b, score_a, self.k)

        self.update_rating(anime_a, new_a)
        self.update_rating(anime_b, new_b)

    def leaderboard(self):
        self.cursor.execute("SELECT name, rating, link FROM animes ORDER BY rating DESC")
        return self.cursor.fetchall()
