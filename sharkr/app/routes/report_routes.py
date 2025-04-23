
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, current_app
from app.extensions import db
from app.models.models import Battle, Startup, Event, Tournament
from app.models.history import BattleEntry

import random

report_bp = Blueprint('reports', __name__, url_prefix='/reports')

@report_bp.route('/')
def index():
    """
    Índice de '/reports'
    """
    #   Pontuação atual das startups
    #   Constrói uma lista de tuplas (nome, pontuação atual)
    startup_points : list[tuple[str, int]] = [];
    for startup in Startup.query.all():
        startup_points.append((startup.name, startup.points));
        
    #   Ordena a lista de startups por pontuação, desc.
    startup_points.sort(key=lambda x: x[1], reverse=True);
    
    #   Eventos registrados
    event_count : list[tuple[str, int, int, int, int, int]] = []
    for startup in Startup.query.all():
        pitch_convincente = 0
        produto_com_bugs = 0
        boa_tracao_de_usuarios = 0
        investidor_irritado = 0
        pitch_fake_news = 0

        #   Seleciona todos os eventos registrados a uma startup
        for event in Event.query.filter_by(startup_id=startup.id).all():
            if event.event_type == "pitch_convincente":
                pitch_convincente += 1
            elif event.event_type == "produto_com_bugs":
                produto_com_bugs += 1
            elif event.event_type == "boa_tracao_usuarios":
                boa_tracao_de_usuarios += 1
            elif event.event_type == "investidor_irritado":
                investidor_irritado += 1
            elif event.event_type == "pitch_fake_news":
                pitch_fake_news += 1

        event_count.append((startup.name, pitch_convincente, produto_com_bugs, boa_tracao_de_usuarios, investidor_irritado, pitch_fake_news))

    #   Ordena a lista de tuplas de inteiros de forma decrescente
    event_count.sort(key=lambda x: x[1], reverse=True)
    
    
    #   Registros de batalhas
    entries: list[tuple[str, str, int, str, int, int]] = []
    for e in BattleEntry.query.all():
        startup_a_name = Startup.query.get(e.startup_a).name
        startup_b_name = Startup.query.get(e.startup_b).name
        winner_name = Startup.query.get(e.winner).name if e.winner else "N/A"
        #   Atualiza o nome do torneio na BattleEntry
        #   Isto deveria ser feito em outro lugar.
        entries.append(("Torneio de Startups (#0001)", startup_a_name, startup_b_name, e.round_number, winner_name, e.startup_a_points, e.startup_b_points))

    
    return render_template('reports/index.html',
                           entries=entries,
                           startups=startup_points,
                           tournaments=[x.name for x in Tournament.query.all()],
                           event_count=event_count,);

#   Relatório com o vencedor do torneio
@report_bp.route('/winner/<int:winner_id>', methods=['GET'])
def winner(winner_id: int):
    """Página para mostrar o vencedor do torneio"""
    winner = Startup.query.get_or_404(winner_id)
    return render_template('reports/winner.html', winner=winner)
