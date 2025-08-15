from anime_elo import AnimeEloDB
import random



# --- Helper Functions ---
def get_input(prompt: str, allow_blank: bool = False, allow_quit: bool = False):
    """
    Helper function to get user input with options to allow blank input or 'q' to quit.
    """
    while True:
        val = input(prompt).strip()
        if allow_quit and val.lower() == 'q':
            return 'q'
        if not val and not allow_blank:
            print("Input cannot be blank.")
            continue
        return val

def match_animes(elo: AnimeEloDB, anime_a: str, anime_b: str) -> bool:
    """
    Returns True if the user chose to quit (q), False otherwise.
    """
    print(f"\nWhich anime do you prefer?")
    print(f"1: {anime_a} ")
    print(f"2: {anime_b} ")
    match_choice = get_input("Enter 1, 2, or 3 (for tie) (q to return to menu): ", allow_blank=False, allow_quit=True)
    if match_choice == "q":
        return True
    try:
        if match_choice == "1":
            elo.match(anime_a, anime_b, winner=anime_a)
        elif match_choice == "2":
            elo.match(anime_a, anime_b, winner=anime_b)
        elif match_choice == "3":
            elo.match(anime_a, anime_b, winner=None)
        else:
            print("Invalid choice, try again.")
            return False
    except Exception as e:
        print(f"Error updating match: {e}")
        return False
    print(f"Updated ratings:")
    print(f"{anime_a}: {elo.get_rating(anime_a)}")
    print(f"{anime_b}: {elo.get_rating(anime_b)}")
    return False

def add_anime_action(elo: AnimeEloDB):
    """
    Add a new anime and optionally match it against existing animes."""
    anime = get_input("Anime name (or 'q' to return to menu): ", allow_quit=True)
    if anime == 'q':
        return
    link = get_input("MAL link: ", allow_blank=True, allow_quit=True)
    if link == 'q':
        return
    link = link if link else None
    try:
        elo.add_anime(anime, link)
        print(f"Added {anime}.")
    except Exception as e:
        print(f"Error adding anime: {e}")
        return
    # Match the new anime against random existing animes until user types 'q'
    while True:
        elo.cursor.execute("SELECT name FROM animes WHERE name != ?", (anime,))
        others = [m[0] for m in elo.cursor.fetchall()]
        if not others:
            print("No other animes to match against.")
            break
        opponent = random.choice(others)
        if match_animes(elo, anime, opponent):
            break

def delete_anime_action(elo: AnimeEloDB):
    """Delete an anime from the database."""
    anime = get_input("Anime name to delete (or 'q' to return to menu): ", allow_quit=True)
    if anime == 'q':
        return
    try:
        elo.delete_anime(anime)
        print(f"Deleted {anime} (if it existed).")
    except Exception as e:
        print(f"Error deleting anime: {e}")

def edit_anime_action(elo: AnimeEloDB):
    anime = get_input("Anime name to edit (or 'q' to return to menu): ", allow_quit=True)
    if anime == 'q':
        return
    # Fetch and display current entry
    try:
        elo.cursor.execute("SELECT name, rating, link FROM animes WHERE name = ?", (anime,))
        entry = elo.cursor.fetchone()
        if not entry:
            print(f"Anime '{anime}' not found.")
            return
        print(f"Current entry:")
        print(f"  Name  : {entry[0]}")
        print(f"  Rating: {entry[1]}")
        print(f"  Link  : {entry[2] if entry[2] else ''}")
    except Exception as e:
        print(f"Error fetching anime: {e}")
        return
    new_name = get_input("New name (leave blank to keep, or 'q' to return to menu): ", allow_blank=True, allow_quit=True)
    if new_name == 'q':
        return
    new_name = new_name if new_name else None
    new_link = get_input("New MAL link (leave blank to keep, or 'q' to return to menu): ", allow_blank=True, allow_quit=True)
    if new_link == 'q':
        return
    new_link = new_link if new_link else None
    try:
        elo.edit_anime(anime, new_name=new_name, new_link=new_link)
        print(f"Edited {anime}.")
    except Exception as e:
        print(f"Error editing anime: {e}")

def retune_leaderboard_action(elo: AnimeEloDB):
    """Randomly match existing animes until user types 'q'."""
    while True:
        elo.cursor.execute("SELECT name FROM animes")
        animes = [m[0] for m in elo.cursor.fetchall()]
        if len(animes) < 2:
            print("Need at least 2 animes for a match.")
            break
        anime_a, anime_b = random.sample(animes, 2)
        if match_animes(elo, anime_a, anime_b):
            break

def leaderboard_action(elo: AnimeEloDB):
    """Display the leaderboard."""
    print("\nLeaderboard:")
    try:
        leaderboard = elo.leaderboard()
        if not leaderboard:
            print("No animes in leaderboard.")
            return
        # Calculate column widths
        name_width = max(len("Name"), max((len(a) for a, _, _ in leaderboard), default=4))
        rating_width = max(len("Rating"), 6)
        link_width = max(len("Link"), max((len(str(l)) for _, _, l in leaderboard if l), default=4))
        # Print header
        print(f"{'Rank':<4}  {'Name':<{name_width}}  {'Rating':>{rating_width}}  {'Link':<{link_width}}")
        print("-" * (8 + name_width + rating_width + link_width))
        # Print rows
        for idx, (anime, rating, link) in enumerate(leaderboard, 1):
            link_str = link if link else ""
            print(f"{idx:<4}  {anime:<{name_width}}  {rating:>{rating_width}.2f}  {link_str:<{link_width}}")
    except Exception as e:
        print(f"Error displaying leaderboard: {e}")

def main():
    elo = AnimeEloDB()
    print("Anime Elo Rating System")
    menu_actions = {
        "1": add_anime_action,
        "2": delete_anime_action,
        "3": edit_anime_action,
        "4": retune_leaderboard_action,
        "5": leaderboard_action
    }
    while True:
        print("\nMenu:")
        print("1. Add anime")
        print("2. Delete anime")
        print("3. Edit anime")
        print("4. Retune leaderboard")
        print("5. Show leaderboard")
        print("q. Quit")
        choice = get_input("Select an option: ", allow_blank=False,  allow_quit=True)
        if choice == 'q':
            print("\nFinal ratings saved in animes.db")
            break
        action = menu_actions.get(choice)
        if action:
            action(elo)
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
