
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
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
    #   Extrai todos os objetos `BattleEntry` do banco de dados
    entries : list[BattleEntry] = BattleEntry.query.all()

    for e in entries:
        flash(f"Startup A: {e.startup_a} | Startup B: {e.startup_b} | Round: {e.round_number} | Winner: {e.winner} | Points A: {e.startup_a_points} | Points B: {e.startup_b_points}", "success");
    
    #   Constrói uma lista de tuplas de inteiros (contagens de quantos eventos de cada tipo uma startup recebeu)
    #   startup_name, "pitch convincente", "produto com bugs", "boa tracao de usuarios", "investidor irritado", "pitch fake news"
    event_count : list[tuple[str, int, int, int, int, int]] = [];
    for startup in Startup.query.all():
        pitch_convincente = 0
        produto_com_bugs = 0
        boa_tracao_de_usuarios = 0
        investidor_irritado = 0
        pitch_fake_news = 0
        
        #   Seleciona todos os eventos registrados a uma startup
        for event in Event.query.all():
            if event.startup_id == startup.id:
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
        event_count.append((startup.name, pitch_convincente, produto_com_bugs, boa_tracao_de_usuarios, investidor_irritado, pitch_fake_news));
        
    #   Ordena a lista de tuplas de inteiros de forma decrescente
    event_count.sort(key=lambda x: x[1], reverse=True)
    
    return render_template('reports/index.html',
                           entries=entries,
                           startups=sorted(Startup.query.all(), key=lambda x: x.get_points(), reverse=True),
                           tournaments=[x.name for x in Tournament.query.all()],
                           event_count=event_count);

#   Relatório com o vencedor do torneio
@report_bp.route('/winner/<int:winner_id>', methods=['GET'])
def winner(winner_id: int):
    """Página para mostrar o vencedor do torneio"""
    winner = Startup.query.get_or_404(winner_id)
    return render_template('reports/winner.html', winner=winner)
