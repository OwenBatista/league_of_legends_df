import pandas as pd
import time
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning) #Suppress SSL warnings

api_key = "RGAPI-9b69e9fb-5740-446b-a5c1-00ea7d505993" 

#Function to retrieve the player's unique identifier (PUUID) given their accountId and region
def get_puuid(accountId, region, api_key):
    
    api_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-account/{accountId}"#Construct the API URL for retrieving summoner information by accountId
    #print("Request URL:", api_url) #Debugging: print the URL being requested
    headers = {"X-Riot-Token": api_key}  #Pass API key in the header for authentication

    resp = requests.get(api_url, headers=headers, verify=False)  #Make a GET request to the API
    player_info = resp.json() #Parse the JSON response
    puuid = player_info['puuid'] #Extract the PUUID from the response

    return puuid #Return the PUUID

#Function to retrieve match IDs given a player's PUUID and mass region
def get_match_ids(puuid, mass_region, no_games, queue_id, api_key):
    
    api_url = f"https://{mass_region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={str(queue_id)}&start=0&count={str(no_games)}" #Construct the API URL for retrieving match IDs associated with the given PUUID
    #print("Request URL:", api_url) #Debugging: print the URL being requested
    headers = {"X-Riot-Token": api_key}  #Pass API key in the header for authentication

    resp = requests.get(api_url, headers=headers, verify=False)  #Make a GET request to the API
    match_ids = resp.json() #Parse the JSON response

    return match_ids #return the list of match IDs

#Function to retrieve detailed match data for a specific match ID
def get_match_data(match_id, mass_region, api_key):
    
    api_url = f"https://{mass_region}.api.riotgames.com/lol/match/v5/matches/{match_id}" #Construct the API URL for retrieving detailed match data
    #print("Request URL:", api_url) #Debugging: print the URL being requested
    headers = {"X-Riot-Token": api_key}  # Pass API key in the header for authentication

    while True: #While statement so that we continuosly loop untils its successful
        resp = requests.get(api_url, headers=headers, verify=False)  #Make a GET request to the API

        if resp.status_code == 429: #whenever we see a 429, we sleep for 10 seconds and then restart from the top of the "while" loop
            print("Rate Limit hit, sleeping for 10 seconds")
            time.sleep(10)
            continue #start the loop again

        match_data = resp.json() #Parse the JSON response

        return match_data #Return the detailed match data

#Function to find player-specific data in the match data using their PUUID
def find_player_data(match_data, puuid):
    participants = match_data['metadata']['participants'] #Extract the list of participants' PUUIDs from the match metadata
    player_index = participants.index(puuid) #Find the index of the player using their PUUID
    player_data = match_data['info']['participants'][player_index] #Extract the player's data from the match information
    return player_data #Return the player's data

#Function to gather player data from all matches into a Dataframe
def gather_all_data(puuid, match_ids, mass_region, api_key):
    #Initialize an empty dictionary to store data for each game
    data = {
        'champion': [],
        'kills': [],
        'deaths': [],
        'assists': [],
        'win': []
    }

    for match_id in match_ids: #Loop through each match ID

        #run the two functions to get the player data from the match ID
        match_data = get_match_data(match_id, mass_region, api_key)
        player_data = find_player_data(match_data, puuid)

        #assign the variables we're interested in
        champion = player_data['championName']
        k = player_data['kills']
        d = player_data['deaths']
        a = player_data['assists']
        win = player_data['win']

        #add them to our dataset
        data['champion'].append(champion)
        data['kills'].append(k)
        data['deaths'].append(d)
        data['assists'].append(a)
        data['win'].append(win)

    df = pd.DataFrame(data) #Convert dictionary to dataframe
    df['win'] = df['win'].astype(int) #Convert win column to integer (0 or 1)

    return df #return the completed Dataframe

#master function that retrieves and processes all necessary player data
def master_function(accountId, region, mass_region, no_games, queue_id, api_key): #Get player's PUUID using accountId and region
    puuid = get_puuid(accountId, region, api_key) #Get player's PUUID using accountId and region
    match_ids = get_match_ids(puuid, mass_region, no_games, queue_id, api_key) #Get recent match IDs
    df = gather_all_data(puuid, match_ids, mass_region, api_key) #Gather full match performance data

    match_id = match_ids[0] #Take the first match ID for retrieving player info
    match_data = get_match_data(match_id, mass_region, api_key) #Get full data for the first match
    player_data = find_player_data(match_data, puuid) #Find the player's specific data in the match
    summoner_name = str(player_data['riotIdGameName']) #Extract and convert the Summoner's name

    return df, summoner_name #Return the complete dataset and player's name

####MAIN PROGRAM####

accountId = 'DMoYao73let_HucAYLrUTyQI4niIZp_ZI0ohwbg5ECQ9pQffgSwXMrE6' #The accountId of the player (replace this with the actual accountId you're querying)
region = 'na1' #The region of the player (e.g., 'na1' for North America)
mass_region = 'americas' #The mass region for match-related queries (e.g., 'americas' for North American matches)
no_games = 90 #Number of games to retrieve (Rate Limits: 20 requests every 1 second, and 100 requests every 2 minutes)
queue_id = 1700 #Arena queue ID (Link to other queue.json: https://static.developer.riotgames.com/docs/lol/queues.json)

df, summoner_name = master_function(accountId, region, mass_region, no_games, queue_id, api_key) #Gather all data into full dataframe and summoner_name
#print(df.sort_values('kills')) #Order your games by amount of kills
#print(df.groupby('champion').mean()) #Get the averages per champion
#print(df.mean(numeric_only=True)) #Find the averages, numeric_only stops it trying to average the "champion" column

##################################################
print("Hello", summoner_name, "from the region of", region.upper()) #Upper to capatilize the region
print("Here are some interesting statistics about your last 90 arena games.")

#create a count column for the number of games player per champion
df['count'] = 1

#The "agg" allows us to get the average of every column but sum the count
champ_df = df.groupby('champion').agg({
    'kills': 'mean',
    'deaths': 'mean',
    'assists': 'mean',
    'win': "mean",
    'count': 'sum'
})

#Reset in the index so we can still use the "champion" column
champ_df.reset_index(inplace=True)

#We limit it to only champions where you've played 2 or more games
champ_df = champ_df[champ_df['count'] >= 2]

#create a kda column
champ_df['kda'] = (champ_df['kills'] + champ_df['assists']) / champ_df['deaths']
champ_df = champ_df.round(2) #Round all numerical values to 2 decimals

#sort the table by kda, starting from the highest
champ_df = champ_df.sort_values('kda', ascending=False) #ascending determines whether its highest to lowest or vice-versa

#assign the first first row and last row to a variable so we can print information about it
best_row = champ_df.iloc[0] #.iloc[0] simply takes the first row in dataframe
worst_row = champ_df.iloc[-1] #.iloc[-1] takes the last row in a dataframe

#Print best and worst performing champions
print("Your best KDA is on", best_row['champion'], "with a KDA of", best_row['kda'], "over", best_row['count'], "game/s")
print("Your worst KDA is on", worst_row['champion'], "with a KDA of", worst_row['kda'], "over", worst_row['count'], "game/s")

#sort by count(games played) instead of KDA
champ_df = champ_df.sort_values('count', ascending=False)

#Get the most played champion
row = champ_df.iloc[0]

#Calculate and format the win rate
win_rate = row['win']
win_rate = str(round(win_rate * 100, 1)) + "%"

#Print most played champion and their winrate
print("Your highest played Champion is", row['champion'], "with", row['count'], "games/s", "and an average Win Rate of", win_rate)

#sort the highest kills in a game (not using the champ_df groupby, using raw data)
highest_kills = df.sort_values('kills', ascending=False)
row = highest_kills.iloc[0]
print("Your highest kill game was with", row['champion'], "Where you had", row['kills'], "kills")

#Display final Dataframe
print(champ_df)
