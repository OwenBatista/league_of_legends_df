# league_of_legends_df
League of Legends DataFrame

"""
This script retrieves, processes, and analyzes player performance data from Riot Games' League of Legends API (specifically for Arena games).

Main functionalities:
- Retrieves a player's PUUID (unique identifier) using their account ID.
- Retrieves a list of recent match IDs played by the user in a specified queue.
- Fetches detailed match data for each match.
- Extracts the player's individual performance statistics (kills, deaths, assists, wins).
- Organizes the data into a structured DataFrame.
- Computes per-champion averages (KDA, win rate, game count) for champions the user played at least twice.
- Identifies and prints:
  - The champion with the best KDA,
  - The champion with the worst KDA,
  - The most played champion and their win rate,
  - The highest kills achieved in a single game.
- Outputs a sorted DataFrame showing per-champion statistics.

The script helps players quickly assess their performance trends and identify their strongest and weakest champions in recent Arena games.
"""
