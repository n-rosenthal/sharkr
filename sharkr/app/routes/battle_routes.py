from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from app.extensions import db
from app.models.models import Battle, Startup, Event

import random

#   Rotas do módulo de BATALHAS
battle_bp = Blueprint('battle', __name__, url_prefix='/battles')

@battle_bp.route('/')
def index():
    """
    Histórico de batalhas
    """
    battles = Battle.query.all();
    return render_template('battles/history.html', battles=battles, startups=Startup.query.all());

#   Entry de uma batalha
@battle_bp.route('/entry/<int:id>', methods=['GET', 'POST'])
def entry(id: int):
    battle = Battle.query.get_or_404(id)
    return render_template('battles/entry.html', battle=battle);

@battle_bp.route('/create/<int:tournament_id>/<int:startup_a_id>/<int:startup_b_id>', methods=['POST'])
def create(tournament_id, startup_a_id, startup_b_id):
    battle = Battle(tournament_id, 1, startup_a_id, startup_b_id, 'in_progress')
    db.session.add(battle)
    db.session.commit()
    return redirect(url_for('tournament.index', id=tournament_id))

#   Rodar uma batalha
@battle_bp.route('/run_battle/<int:id>', methods=['POST'])
def run_battle(id: int) -> Response:
    battle = Battle.query.get_or_404(id)
    battle.run_battle();
    return redirect(url_for('tournament.index', id=battle.id))

#   Inserir um evento à uma startup, durante uma batalha
@battle_bp.route('/insert_event/<int:battle_id>/<int:startup_id>/<string:event_type>', methods=['GET', 'POST'])
def insert_event(battle_id, startup_id, event_type):
    #   Verifica se a startup apontada por `startup_id` já recebeu um evento do tipo `event_type` durante a batalha apontada por `battle_id`
    #   Só é possível receber uma unidade por tipo de evento, por batalha
    try:
        event = Event.query.filter_by(startup_id=startup_id, event_type=event_type, battle_id=battle_id).first()
        if event is not None:
            raise Exception()
    except Exception:
        flash('Startup ja recebeu um evento desse tipo nesta batalha', 'danger')
    
    if event is None:
        event = Event(user_id=1,
                      startup_id=startup_id,
                      event_type=event_type,
                      battle_id=battle_id)
        db.session.add(event)
        db.session.commit()
    
    return redirect(url_for('tournament.index', id=battle_id))

#   Show
@battle_bp.route('/show/<int:id>')
def show(id: int):
    battle = Battle.query.get_or_404(id)
    return render_template('battles/show.html', battle=battle);
