# Anime Elo Ranker

A simple Python application to rank anime using the Elo rating system. Compare animes in pairs, update their ratings based on your preferences, and maintain a persistent leaderboard using SQLite.

## Features

- Add, edit, or delete anime entries (with optional MyAnimeList links)
- Compare animes in random matchups or focus on a newly added anime
- Elo rating system for fair ranking
- Persistent storage with SQLite
- Command-line menu interface
- Formatted leaderboard display

## Requirements

- Python 3.7+
- SQLite (included with Python standard library)

## Usage

- Follow the on-screen menu to add, edit, delete, or compare animes.
- When comparing, enter `1`, `2`, or `3` (for a tie) to choose your preferred anime, or `q` to return to the main menu.
- The leaderboard shows all animes ranked by their Elo rating.

## Database

- Anime data is stored in `animes.db` (SQLite).
- You can view or edit the database with any SQLite GUI (e.g., DB Browser for SQLite).

## Git & Collaboration

- To contribute, fork the repo and submit a pull request.
- Add `__pycache__/` and `animes.db` to your `.gitignore` if you don't want to track them.

Made with ❤️ by okarioto
