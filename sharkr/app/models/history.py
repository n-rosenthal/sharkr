""" sharkr/app/models/history.py
    Implementação da classe `BattleEntry`, registro de batalhas que ocorreram no torneio atual ou em torneios anteriores.
"""
from app.extensions import db
from flask import render_template
from sqlalchemy import func as sql_func


class BattleEntry(db.Model):
    __tablename__ = 'battle_entry'
    id = db.Column(db.Integer, primary_key=True)
    startup_a = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    startup_b = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    tournament_name = db.Column(db.String(255), nullable=False);
    round_number = db.Column(db.Integer, nullable=False)
    winner = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=True)
    startup_a_points = db.Column(db.Integer, nullable=False)
    startup_b_points = db.Column(db.Integer, nullable=False)
    startup_a_events = db.Column(db.JSON, nullable=False, default=list)
    startup_b_events = db.Column(db.JSON, nullable=False, default=list)
    
    def __init__(self, startup_a, startup_b, tournament_name, round_number, winner, startup_a_points, startup_b_points, startup_a_events, startup_b_events):
        self.startup_a = startup_a
        self.startup_b = startup_b
        self.tournament_name = tournament_name
        self.round_number = round_number
        self.winner = winner
        self.startup_a_points = startup_a_points
        self.startup_b_points = startup_b_points
        self.startup_a_events = startup_a_events
        self.startup_b_events = startup_b_events
        
        db.session.add(self)
        db.session.commit();
        return;
    
    def __repr__(self):
        return '<BattleEntry %r>' % self.id
    
    def render(self):
        return render_template('battles/entry.html', entry=self);