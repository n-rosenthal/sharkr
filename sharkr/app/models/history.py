import random;
from itertools import combinations;
from datetime import datetime;

from app.extensions import db

from flask import flash, redirect, render_template, url_for, current_app
from sqlalchemy import and_, or_, func as sql_func
from app.models.models import Startup, Battle, Event, Tournament


class BattleEntry(db.Model):
    __tablename__ = 'battle_entry'
    id = db.Column(db.Integer, primary_key=True)
    startup_a = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    startup_b = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    winner = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=True)
    startup_a_points = db.Column(db.Integer, nullable=False)
    startup_b_points = db.Column(db.Integer, nullable=False)
    startup_a_events = db.Column(db.JSON, nullable=False, default=list)
    startup_b_events = db.Column(db.JSON, nullable=False, default=list)
    
    def __init__(self, startup_a, startup_b, tournament_id, round_number, winner, startup_a_points, startup_b_points, startup_a_events, startup_b_events):
        self.startup_a = startup_a
        self.startup_b = startup_b
        self.tournament_id = tournament_id
        self.round_number = round_number
        self.winner = winner
        self.startup_a_points = startup_a_points
        self.startup_b_points = startup_b_points
        self.startup_a_events = startup_a_events
        self.startup_b_events = startup_b_events
        
        db.session.add(self)
        db.session.commit();
        return; 