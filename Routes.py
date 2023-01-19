from flask import Blueprint, render_template
from Login import AccessAccount

views = Blueprint(__name__, "views")
access_token = ""

@views.route("/home")
def home():
    global access_token
    if access_token == "":
        get_token = AccessAccount()
        access_token = get_token.getAccessToken()
        print(access_token)
        return render_template("HomePage.html")
    else:
        return render_template("HomePage.html")

@views.route("/mood_analysis")
def moodAnalysis():
    return render_template(("MoodAnalysis.html"))

@views.route("/data_analysis")
def dataAnalysis():
    return render_template(("DataAnalysis.html"))

@views.route("/song_mood")
def songMood():
    return render_template(("SongMood.html"))

@views.route("/data_set")
def dataSet():
    return render_template(("DataSet.html"))