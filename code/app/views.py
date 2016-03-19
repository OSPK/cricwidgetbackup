from app import app
from app import cache
from flask import redirect, url_for, render_template, flash, request, json,\
    jsonify, Response, escape, abort
import urllib
import json
import iso8601
import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from random import random
import requests
import os
from flask import Flask, render_template
from flask.ext.basicauth import BasicAuth

app.config['BASIC_AUTH_USERNAME'] = 'waqas'
app.config['BASIC_AUTH_PASSWORD'] = 'dailypak123'

basic_auth = BasicAuth(app)

app.jinja_env.globals.update(random=random)
# ======================================================= Jobs and Cron and Such


def del_cache():
    # Do your work here
   cache.delete_memoized(getresponse)
   print "cache deleted"


scheduler = BackgroundScheduler()
scheduler.add_job(del_cache, 'interval', id='del_cache', seconds=15)
scheduler.start()


# ======================================================= /Jobs and Cron and Such

# ======================================================= When the app exits


@atexit.register
def goodbye():
    scheduler.remove_job("del_cache")
    # scheduler.remove_all_jobs()
    scheduler.shutdown()
    print "Goodbye!"


# ======================================================= /When the app exits

# ======================================================= Functions


def yquery(query):
    base_url = "http://query.yahooapis.com/v1/public/yql?q="
    end_url = "&format=json&env=store%3A%2F%2F0TxIGQMQbObzvU4Apia0V0"
    return base_url + query + end_url


def appify(template, **kwargs):
    if request.args.get('type') == 'json':
        return jsonify(**kwargs)
    else:
        return render_template(template, **kwargs)


@cache.memoize(50)
def getresponse(turl):
    # response = urllib.urlopen(turl)
    response = requests.get(turl)
    return json.loads(response.text)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def team(query, id):
    teams = query.get('teams')
    pteams = {}
    for team in teams:
        pteams[team['i']] = team['fn']
    return pteams.get(id)


def player(query, id):
    players = {}
    for team in query.get('teams'):
        teamid = team['i']
        for player in team['squad']:
            players[player['i']] = {'name': player['short'], 'team': teamid}

    return players.get(id)


def flag(query, teamid):
    flags = {}
    for team in query.get('teams'):
        tid = team.get('i')
        if tid == teamid:
            flags = team.get('flag')

    return flags


def format_datetime(value, format='medium'):
    date = iso8601.parse_date(str(value))
    date = date - datetime.timedelta(minutes=30)
    if format == 'full':
        return date.strftime("%d %b %Y, %H:%M %z")
    elif format == 'medium':
        return date.strftime("%d %b %Y, %H:%M")


def is_list(value):
    return isinstance(value, list)

app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['is_list'] = is_list
app.jinja_env.globals.update(team=team, player=player, flag=flag)


# ======================================================= /Functions

# ======================================================= Routes

@cache.cached(timeout=15)
@app.route("/")
def index():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    return appify('index.html', links=links)


@app.route("/psl")
def psl():
    return render_template("psl.html")


@cache.cached(timeout=5)
@app.route("/ongoin_series")
def ongoing_series():
    url = yquery('SELECT * FROM cricket.series.ongoing')
    result = getresponse(url)
    series = result['query']['results']['Series']
    serieses = []
    for serie in series:
        m = {'id': serie['SeriesId'], 'name': serie['SeriesName'], 'teams': serie['Participant']['Team']}
        serieses.append(m)

    return appify('ongoing_series.html', serieses=serieses)


@cache.cached(timeout=5)
@app.route("/upcoming_matches")
def upcoming_matches():
    url = yquery('SELECT * FROM cricket.upcoming_matches')
    result = getresponse(url)
    matches = result['query']['results']['Match']

    return appify('upcoming_matches.html', matches=matches)


@cache.cached(timeout=5)
@app.route("/ongoing_matches")
def ongoing_matches():
    url = yquery('SELECT mid, teams FROM cricket.scorecard.live.summary')
    result = getresponse(url)
    matches = result.get('query').get('results')
    if matches is None:
        return redirect(url_for('upcoming_matches'))
    else:
        matches = result.get('query').get('results').get('Scorecard')
    if not isinstance(matches, list):
        mitch = []
        mitch.append(matches)
        matches = mitch
    return appify('ongoing_matches.html', matches=matches)


@cache.cached(timeout=15)
@app.route("/match/<int:mid>/")
def match(mid):
    url = yquery('select * from cricket.scorecard.live WHERE mid="{}"'.format(mid))
    result = getresponse(url)
    scorecard = result.get('query').get('results')

    if scorecard is None:
        url2 = yquery('select * from cricket.scorecard WHERE match_id="{}"'.format(mid))
        result = getresponse(url2)
        scorecard = result.get('query').get('results').get('Scorecard')
        if scorecard['past_ings'] is None:
            url = yquery('SELECT * FROM cricket.upcoming_matches')
            result = getresponse(url)
            matches = result['query']['results']['Match']
            return appify('match_small.html', notstarted=True, scorecard=scorecard, mid=mid, matches=matches)
    else:
        scorecard = result['query']['results']['Scorecard']

    if not isinstance(scorecard.get('past_ings'), list):
        iings = []
        iings.append(scorecard.get('past_ings'))
        scorecard['past_ings'] = iings

    if request.args.get('size') == 'small':
        return appify('match_small.html', scorecard=scorecard, mid=mid)

    return appify('match.html', scorecard=scorecard, mid=mid)


@app.route("/delete_cache")
def delete_cache():
    cache.delete_memoized(getresponse)
    return "deleted"


@app.route("/pakind")
def pakind():
    return render_template("pakind.html")


@app.route("/update")
@basic_auth.required
def pakind_update():
    return render_template("pakind-update.html")


@app.route("/pakind_submit", methods=['POST'])
@basic_auth.required
def pakind_submit():
    pakscore = str(request.form.get('pakscore'))
    pakovers = str(request.form.get('pakovers'))
    pakstatus = str(request.form.get('pakstatus'))

    indscore = str(request.form.get('indscore'))
    indovers = str(request.form.get('indovers'))
    indstatus = str(request.form.get('indstatus'))

    board = """{{
        "Pakistan": {{
            "status":"{ps}",
            "score":"{psc}",
            "overs":"{po}"
        }},
        "India": {{
            "status":"{iis}",
            "score":"{isc}",
            "overs":"{io}"
        }}
    }}""".format(ps=pakstatus, psc=pakscore, po=pakovers, iis=indstatus, isc=indscore, io=indovers)


    with open('code/app/static/pakind.json', 'w') as file:
        file.write(board)

    return redirect(url_for('pakind_update'))