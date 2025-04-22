
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from app.extensions import db
from app.models.models import Battle, Startup, Event

import random

report_bp = Blueprint('reports', __name__, url_prefix='/reports')

@report_bp.route('/')
def index():
    """
    Índice de '/reports'
    """
    return render_template('reports/index.html')

#   Relatório com o vencedor do torneio
@report_bp.route('/winner/<int:winner_id>', methods=['GET'])
def winner(winner_id: int):
    """Página para mostrar o vencedor do torneio"""
    winner = Startup.query.get_or_404(winner_id)
    return render_template('reports/winner.html', winner=winner)
