from Login import AccessAccount
from Functions import Functions
import requests
import time
import pandas as pd

class GatherData(Functions):
  def __init__(self, mood1, mood2):
      get_token = AccessAccount()
      self.access_token = get_token.getAccessToken()
      self.moods = [mood1, mood2]
      self.playlists = self.listOfPlaylists()

  def getCsvFile(self):
      for c in range(len(self.moods)): # Loops through both moods to be compared
          mood = self.moods[c] # Selects the first mood
          playlist_ids = []
          for i in range(len(self.playlists)):
              if mood in self.playlists[i]["name"].lower():
                  playlist_ids.append(self.playlists[i]["id"])
          # Appends all playlists from Spoifty account (retrieved through the method in the Functions class) that contain the target emootion into an array containing the ID's of said playlists
          song_ids = []
          for z in range(len(playlist_ids)): # Loops through all playlists in the array generated previously
              list_of_songs_in_playlist_temp = requests.get("https://api.spotify.com/v1/playlists/" + playlist_ids[z] + "/tracks",
                                                            headers={"Authorization": "Bearer " + self.access_token})
              song_objects = list_of_songs_in_playlist_temp.json()["items"]
              # A get request is made to the Spotify API to retrieve song objects for each song in the playlist
              for n in range(len(song_objects)):
                  song_ids.append(song_objects[n]["track"]["id"])
                  print(song_objects[n]["track"]["name"])
              # For each song object the song ID is retrieved and appened to an array called song_ids
          for j in range(len(song_ids)): # Each song from song_ids is looped through
              audio_features_get = requests.get("https://api.spotify.com/v1/audio-features?ids=" + song_ids[j],
                                                headers={"Authorization": "Bearer " + self.access_token})
              audio_features = audio_features_get.json()["audio_features"]
              audio_features_dict = audio_features[0]
              # A get request is made to the Spotify API to retrieve the audio features for each song
              for g in range(7):
                  audio_features_dict.popitem() # Irrelevant audio features are removed
              if j == 0:
                  song_stats = pd.DataFrame(data=audio_features_dict, index=[0]) # During the first iteration and empty dataframe for all the audio features is made
              else:
                  song_stats_temp = pd.DataFrame(data=audio_features_dict, index=[0])
                  song_stats = pd.concat([song_stats, song_stats_temp], ignore_index=True)
                  # The audio features for each song is added to the song_stats dataframe
              time.sleep(0.1) # Reduces the rate at which Spotify API requests are made so that the limit of requests isnt exceeded
          song_stats.to_csv(mood+"_song_stats.csv")
          # The song_stats dataframe for each mood is saved as a csv file


coolandcringe = GatherData("cool","cringe")
coolandcringe.getCsvFile()
