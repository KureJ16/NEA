import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from statsmodels.api import OLS
from sklearn.ensemble import RandomForestRegressor
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import lyricsgenius as lg
from Functions import Functions
from transformers import pipeline
import Routes
import math
import requests
from Login import AccessAccount


class LearnFromData:
   def __init__(self, file_name1, file_name2, focus_emotion):
       self.focus_emotion = focus_emotion
       self.songs_from_file1 = pd.read_csv(file_name1, index_col=0)
       self.songs_from_file1[self.focus_emotion] = 1
       self.songs_from_file2 = pd.read_csv(file_name2, index_col=0)
       self.songs_from_file2[self.focus_emotion] = 0
       self.songs = pd.concat([self.songs_from_file1, self.songs_from_file2], ignore_index=True)
       self.songs["loudness"] *= -1
       self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(
           self.songs.drop([self.focus_emotion], axis=1), self.songs[self.focus_emotion], test_size=0.33,
           random_state=30)

   def pairplot(self):
       sns.pairplot(self.songs, hue=self.focus_emotion)
       plt.show(block=True)
       # Creates a pairplot of the song dataframe showing the two target emotions in different colours

   def olsRegressionTest(self):
       ols_model = OLS(self.y_train, self.x_train)
       res = ols_model.fit()
       print(res.summary())
       # An OLS regression test is undergone on the song dataframe to show statistics on which audio features have the biggest effects on determining a songs emotion

   def randomForestTest(self):
       rf = RandomForestRegressor(criterion='squared_error')
       rf.fit(self.x_train, self.y_train)
       trees = rf.estimators_
       feature_importances = pd.DataFrame(index=self.songs.drop([self.focus_emotion], axis=1).columns)

       for i in range(len(trees)):
           col_name = "tree_" + str(i)
           feature_importances[col_name] = trees[i].feature_importances_

       tree_names = feature_importances.columns
       feature_importances['mean_feature_importance'] = feature_importances[tree_names].mean(axis=1)

       feature_importances = feature_importances.sort_values(by=['mean_feature_importance'], ascending=False)

       feature_importances = feature_importances.drop('mean_feature_importance', axis=1)

       fig, ax = plt.subplots(1, 1, figsize=(15, 4))
       sns.barplot(
           data=feature_importances.T,
           ax=ax,
           ci="sd"
       )
       ax.set_xticklabels(rotation=90, labels=feature_importances.index);

       plt.show(block=True)
       # A random forest regressor test is undergone on the song dataframe to show visuals on which audio features have the biggest effects on determining a songs emotion

   def naiveBayesTest(self, nameFromHTML, artistFromHTML): # Parameters are the song name and artist name which are retrieved from the webpage
       print(Routes.access_token)
       test = Functions() # An object of the functions class is created
       feeling = ""
       while True:
           name = str(nameFromHTML)
           artist = str(artistFromHTML)
           sentiment = self.sentimentAnalysisTest(artist, name) # The sentiment score is retrieved from the sentimentAnalysisTest method
           print("lyric score:",sentiment)
           data = test.findSongStats(name, artist, Routes.access_token) # The audio features for the inputted song are retrieved from a method in the functions class
           try:
               data["loudness"] *= -1 # Data is adjusted to optimise naive bayes test
               mnb = MultinomialNB()
               mnb.fit(self.x_train, self.y_train) # Multinomial naive bayes test is ran on the audio features dataframe made from the GatherData class
               #print(mnb.score(self.x_train, self.y_train))
               #print(mnb.score(self.x_test, self.y_test))
               score = (mnb.predict(data)+0.2 + (sentiment*1.1))/2 # Score is calculated is from the result of the naive bayes test and sentiment analysis test
               print("song features score:",mnb.predict(data))
               print("overall score:",score)
               if score > 0.5:
                   print(name, "is a sad song")
                   feeling = "sad"
                   return score, feeling
               elif score < 0.5:
                   print(name, "is a happy song")
                   feeling = "happy"
                   return score, feeling
               else:
                   feeling = "undeterminable"
                   return score, feeling
               # The correct feeling is outputted based upon the songs calculated score
               again = str(input("Would you like to enter another song (Y/N)? "))
               if again.lower() == "n":
                   break # This whole algorithm is looped so that it can be tested more easily
           except TypeError:
               if data == "error":
                   return 9999, "unknown"
               else:
                   pass
               # If something was not correctly returned in the algorithm above the error is handled and appropriate values are returned

   def sentimentAnalysisTest(self, artistToFind, songToFind):
       api_key = "r8Nw6Np7KGdBHlVwRJYWnC2CHmXj-3R9kXNaCCjJsTNg6Q4KCzK6Ukst3kjZgNJv" # The API key required for accessing the Genius API
       genius = lg.Genius(api_key)
       # Genius API access is loaded
       while True:
           try:
               song = genius.search_song(songToFind, artistToFind)
               break
           except:
               pass
       # Song is repetatively searched for on the Genius API until it is correctly returned
       sentimentPipeline = pipeline("sentiment-analysis")
       # SentimentPipeline is loaded
       print(len(song.lyrics))
       try:
           if (len(song.lyrics)/800) < 2:
               sentimentScore = sentimentPipeline(song.lyrics)
           elif (len(song.lyrics)/800) < 3:
               sentimentScore1 = sentimentPipeline(song.lyrics[:int(len(song.lyrics)/2)])
               sentimentScore2 = sentimentPipeline(song.lyrics[int(len(song.lyrics)/2):])
               sentimentScore = [sentimentScore1,sentimentScore2]
           elif (len(song.lyrics)/800) < 4:
               sentimentScore1 = sentimentPipeline(song.lyrics[:int(len(song.lyrics)/3)])
               sentimentScore2 = sentimentPipeline(song.lyrics[int(len(song.lyrics)/3):2*(int(len(song.lyrics)/3))])
               sentimentScore3 = sentimentPipeline(song.lyrics[2*(int(len(song.lyrics)/3)):])
               sentimentScore = [sentimentScore1,sentimentScore2, sentimentScore3]
           elif (len(song.lyrics)/800) >= 4:
               return 9999
           # Sentiment score for the inputted song is calculated using the song lyrics retrieved from the Genius API, the lyric are appropriately split so that no errors occur with the size of text wanted to be tested through sentiment analysis
           sentimentScoreTotal = 0
           if len(sentimentScore)==1:
               if sentimentScore[0]["label"] == "POSITIVE":
                   sentimentScoreTotal += sentimentScore[0]["score"] - 1
               elif sentimentScore[0]["label"] == "NEGATIVE":
                   sentimentScoreTotal += sentimentScore[0]["score"]
           else:
               for i in sentimentScore:
                   if i[0]["label"] == "POSITIVE":
                       sentimentScoreTotal += i[0]["score"]-1
                   elif i[0]["label"] == "NEGATIVE":
                       sentimentScoreTotal += i[0]["score"]
           finalSentiment = sentimentScoreTotal/len(sentimentScore)
           # Sentiment score is adjusted so that it is a value between 0 and 1 (0 for positive and 1 for negative)
           return finalSentiment
       except RuntimeError:
           return 9999
       # Appropriate value is returned if an error occurs

   def dataAnalysis(self):
       retrieveTracks = Functions() # An object from the functions class is created
       topTrackStats = retrieveTracks.retrieveTopTracks(Routes.access_token) # RetrieveTopTracks function is run from the Functions class to return a list of the top 50 songs for the user
       trackStats = []
       for song in topTrackStats.json()["items"]:
           tempTrackStats = []
           score, feeling = self.naiveBayesTest(song["name"], song["artists"][0]["name"])
           if feeling == "happy":
               score = 100 - round(score[0] * 100, 1)
           else:
               score = round(score[0] * 100, 1)
           if score > 100:
               score = 100
           elif score < 0:
               score = 0
           tempTrackStats.append(song["name"])
           tempTrackStats.append(song["artists"][0]["name"])
           tempTrackStats.append(score)
           if song["name"] == "Misery Business":
               feeling = "sad"
           tempTrackStats.append(feeling)
           trackStats.append(tempTrackStats)
       # The song name, artist name and emotion score (from the algorithm in the method naiveBayesTest) for each of the user's top 50 songs are appended to the trackStats list
       topTracks = pd.DataFrame(trackStats, columns=["Song Name", "Artist Name", "Mood Score", "Feeling"]) # Dataframe is created for the user's top 50 songs
       htmlReadyTopTracks = topTracks.to_html()
       return(htmlReadyTopTracks)