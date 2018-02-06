#This app uses the nba python api and displays relevant data
from flask import Flask, render_template, request, redirect, url_for
import nba_py
import requests
from datetime import datetime, timedelta

#date variables
today = datetime.today()
yesterday = datetime.today() - timedelta(1)

#start app
app = Flask(__name__)

#helper functions
def game_data(teams, points):
    ''' This function formats game data so that its easy to print.
    Input:  teams - list of teams.
            points - list of points.
    Output: games - list of formatted games.
            (eg. [team1 vs team2, pt1 - pt2, winner])
    '''
    games = []
    for i in range(len(teams)):
        if i % 2 == 1:
            game = str(teams[i])+' vs '+str(teams[i-1])
            points1 = points[i]
            points2 = points[i - 1]
            gamePoints = str(points[i])+' - '+str(points[i-1])
            try:
                if points1 > points2:
                    winner = teams[i]
                else:
                    winner = teams[i - 1]
            except:
                winner = "NA"
            games += [[game, gamePoints, winner]]
    return games

#routes
#home page
@app.route('/')
def index():
    scoreboard = nba_py.Scoreboard()
    linescore = scoreboard.line_score()
    teams = list(linescore['TEAM_ABBREVIATION'])
    points = list(linescore['PTS'])
    games = game_data(teams, points)
    MAX = len(games)
    date = today.date()
    return render_template('index.html', games = games, max = MAX, today=date)

#process route, when user submits a date
@app.route('/process', methods=['POST'])
def process():
    date = request.form['date']
    day = int(date[8:10])
    month = int(date[5:7])
    year = int(date[0:4])
    scoreboard = nba_py.Scoreboard(day=day, month=month, year=year)
    linescore = scoreboard.line_score()
    teams = list(linescore['TEAM_ABBREVIATION'])
    points = list(linescore['PTS'])
    games = game_data(teams, points)
    MAX = len(games)
    return render_template('index.html', games = games, max = MAX, today=date)

if __name__ == '__main__':
    app.run(debug=True)
