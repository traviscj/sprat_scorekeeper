
from peewee import *
import os
import binascii

db = SqliteDatabase('sprat.db')

class BaseModel(Model):
    def __repr__(self):
        return str(self._data)
    class Meta:
        database = db

class Game(BaseModel):
    token = CharField(unique = True)

#class Player(BaseModel):
#    name = CharField()
    
#class GamePlayer(BaseModel):
#    player_id = 

class Round(BaseModel):
    game_token = CharField()
    game_round = IntegerField()
    player_name = CharField()
    score = IntegerField()

db.connect()
# db.create_tables([Game, Round])

def new_game():
    tok = binascii.b2a_hex(os.urandom(5))
    g = Game.create(token=tok)
    g.save()
    return tok

def new_round_score(token, round, player, score):
    r1t = Round.create(game_token=token, game_round=round, player_name=player, score=score)
    r1t.save()

from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)

@app.route('/')
def hello_world():
#    return 'Hello World! {token}'.format(token=new_game())
    token = new_game()
    return redirect(url_for('game', token=token))

@app.route('/<token>')
def game(token):
    res = (Round.select()
       .where(Round.game_token == token)
       .execute())
    players = []
    player_scores = {}
    rounds = []
    for r in res:
        if r.player_name not in players:
            players.append(r.player_name)
        if r.game_round not in rounds:
            rounds.append(r.game_round)
        if r.player_name in player_scores:
            player_scores[r.player_name][r.game_round] = r.score
        else:
            player_scores[r.player_name] = {}
            player_scores[r.player_name][r.game_round] = r.score
    print player_scores
    return render_template('scores.html', players=players, rounds=rounds, player_scores=player_scores)

@app.route("/add_score/<token>/<round>/<player>/<score>")
def add_score(token, round, player, score):
    new_round_score(token, round, player, score)
    return "added"

@app.route('/add_score_form/<token>')
def add_score_form(token):
    return render_template('add_score.html', token=token, players=["traviscj", "anjorges", "pauljoos"])

@app.route('/add_score_post', methods=['POST'])
def add_score_post():
    token = request.form['token']
    round = request.form['round']
    player = request.form['player']
    score = request.form['score']
    print token, round, player, score
    new_round_score(token, round, player, score)
    return "added"

if __name__ == '__main__':
    app.run(debug=True, port=3456)
