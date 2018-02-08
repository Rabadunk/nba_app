#This app uses the nba python api and displays relevant data
from flask import Flask, render_template, request, redirect, url_for
import nba_py
import requests
import pygal
from pygal.style import DarkStyle, NeonStyle, LightSolarizedStyle
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
            game = str(teams[i-1])+' vs '+str(teams[i])
            points1 = points[i-1]
            points2 = points[i]
            gamePoints = str(points[i-1])+' - '+str(points[i])
            try:
                if points1 > points2:
                    winner = teams[i - 1]
                else:
                    winner = teams[i]
            except:
                winner = "NA"
            games += [[game, gamePoints, winner]]
    return games

def graph_gen(linescore):
    ''' This function formats game data so that its easy to print.
    Input:  linescore - table containing todays data.
    Output: graph_data - list of 3 graphs, 1 line graph and 2 bar graphs.
            (eg. [line, bar1, bar2])
    '''
    teams = list(linescore['TEAM_ABBREVIATION'])
    q1 = list(linescore['PTS_QTR1'])
    q2 = list(linescore['PTS_QTR2'])
    q3 = list(linescore['PTS_QTR3'])
    points = list(linescore['PTS'])
    q4 = []
    teamScores = []
    graph_data = []
    try:
        for i in range(len(q1)):
            q4 += [points[i] - (q1[i] + q2[i] + q3[i])]
            q4 += [points[i] - (q1[i] + q2[i] + q3[i])]
            teamScores += [[0, q1[i], q2[i], q3[i], q4[i]]]

        for i in range(len(teams)):
            if i % 2 == 1:
                line_chart = pygal.Line(fill=True, style=LightSolarizedStyle)
                line_chart.title = 'Points by Quarter'
                line_chart.x_labels = map(str, range(0, 5))
                line_chart.add(teams[i-1], teamScores[i-1])
                line_chart.add(teams[i], teamScores[i])
                line_chart = line_chart.render_data_uri()

                turnover = list(linescore['TOV'])
                assist = list(linescore['AST'])
                rebound = list(linescore['REB'])
                bar_chart1 = pygal.Bar(style=LightSolarizedStyle)
                bar_chart1.title = teams[i-1] +' game stats'
                bar_chart1.add('TOV', turnover[i-1])
                bar_chart1.add('AST', assist[i-1])
                bar_chart1.add('REB', rebound[i-1])
                bar_chart1 = bar_chart1.render_data_uri()

                bar_chart2 = pygal.Bar(style=LightSolarizedStyle)
                bar_chart2.title = teams[i] +' game stats'
                bar_chart2.add('TOV', turnover[i])
                bar_chart2.add('AST', assist[i])
                bar_chart2.add('REB', rebound[i])
                bar_chart2 = bar_chart2.render_data_uri()
                graph_data += [[line_chart, bar_chart1, bar_chart2]]

        return graph_data
    except:
        for i in range(len(teams)):
            if i % 2 == 1:
                xyn_chart = pygal.XY(style=NeonStyle)
                xyn_chart.title = 'NO DATA YET, EVERYBODY PANIC!!!'
                xyn_chart.add('THERES',  [(1, -5), (1, 5)])
                xyn_chart.add('NO', [(x, -5*x + 10) for x in range(1, 4)])
                xyn_chart.add('DATA',  [(3, -5), (3, 5)])
                xyn_chart = xyn_chart.render_data_uri()

                xya_chart = pygal.XY(style=NeonStyle)
                xya_chart.title = 'NO DATA YET, EVERYBODY PANIC!!!'
                xya_chart.add('THERES',  [(-1.8, 1), (1.8, 1)])
                xya_chart.add('NO', [(x, -5*x + 10) for x in range(0, 4)])
                xya_chart.add('DATA', [(x, 5*x + 10) for x in range(-3, 1)])
                xya_chart = xya_chart.render_data_uri()

                graph_data += [[xyn_chart, xya_chart, xyn_chart]]
        return graph_data

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
    graph_data = graph_gen(linescore)
    return render_template('index.html', games = games, max = MAX, today=date, graph_data = graph_data)

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
    graph_data = graph_gen(linescore)
    return render_template('index.html', games = games, max = MAX, today=date, graph_data = graph_data)


if __name__ == '__main__':
    app.run(debug=True)
