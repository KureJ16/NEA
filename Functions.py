import requests
import pandas as pd
from Login import AccessAccount

class Functions(AccessAccount):
   def __init__(self):
       self.user_id = ""

   def getUserID(self, access_token):
       openr = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": "Bearer " + access_token}) #Get request is made to collect user ID
       self.user_id = openr.json()["id"] #User ID is collect from the JSON response from the get request

   def addPlaylist(self, name, public_status, description, access_token):
       self.getUserID() #Collects user ID from getUserID function
       playlistr = requests.post("https://api.spotify.com/v1/users/" + self.user_id + "/playlists",
                                 headers={"Authorization": "Bearer " + access_token},
                                 json={"name": name, "public": public_status, "description": description}) #Post request is made to be able to add a playlist with specified name, public status and description

   def findSongStats(self, song_name, song_artist, access_token):
       song_id = ""
       song_json = requests.get("https://api.spotify.com/v1/search?q=" + song_name.lower() + "&type=track",
                                headers={"Authorization": "Bearer " + access_token})
       # Get request is made to retrieve JSON response based on the song name that the user has inputted
       for n in range(len(song_json.json()["tracks"]["items"])):
           if (song_json.json()["tracks"]["items"][n]["name"].lower() == song_name.lower()) and (
                   song_json.json()["tracks"]["items"][n]["album"]["artists"][0][
                       "name"].lower() == song_artist.lower()):
               song_id = song_json.json()["tracks"]["items"][n]["id"]
               break
       # JSON response is looped through to return the song ID for the song that matches the correct song name and artist name
       try:
           audio_features_retreived = requests.get("https://api.spotify.com/v1/audio-features?ids=" + song_id,
                                                   headers={"Authorization": "Bearer " + access_token})
           audio_features_for_song = audio_features_retreived.json()["audio_features"][0]
           # Audio features for song are retrieved from get request to Spotify API and stored in an array
           for g in range(7):
               audio_features_for_song.popitem()
           # Irrelevant audio features are removed from the array
           test_song_data = pd.DataFrame(data=audio_features_for_song, index=[0]) #Song audio features array is converted to a single row data frame
           return test_song_data
       except AttributeError:
           print("Song not found")
           return "error"
       # If song is not on Spotify then “Song not found” is printed and an appropriate error message is returned so the error can be appropriately handled

   def listOfPlaylists(self, access_token):
       self.getUserID() #Collects user ID from getUserID function
       list_of_playlists = requests.get("https://api.spotify.com/v1/users/" + self.user_id + "/playlists",
                                        headers={"Authorization": "Bearer " + access_token})
       # Get request is made to return a list of user’s playlists
       return list_of_playlists.json()["items"]

   def retrieveTopTracks(self, access_token):
       statr = requests.get("https://api.spotify.com/v1/me/top/tracks?limit=10&time_range=long_term",
                            headers={"Authorization": "Bearer " + access_token})
       # Get request is made to return a user's top 50 tracks
       return statr