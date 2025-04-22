from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.models import Tournament, Startup, Battle, Event
from app import app

tournament_bp = Blueprint('tournament', __name__, url_prefix='/tournament')

@tournament_bp.route('/', methods=['GET'])
def index():
    """
    Página de listagem de torneios
    
    current_tournament: Torneio em andamento
    battles: Batalhas do torneio em andamento
    tournament_winner: Vencedor do torneio
    """
    try:
        tournament = db.session.query(Tournament).filter(Tournament.status.in_(['completed', 'in_progress'])).first()

        if tournament:
            if tournament.status == 'completed':
                return render_template('tournament/index.html', 
                                       current_tournament=tournament, 
                                       tournament_winner=tournament.winner, 
                                       battles=tournament.battles)
            
            if tournament.status == 'in_progress':
                if tournament:
                    with app.app_context():
                        tournament.next_round(tournament.round_winners())
                    return render_template('tournament/index.html', current_tournament=tournament, battles=tournament.battles);
                else:
                    return render_template('tournament/index.html');
            
    except Exception as e:
        flash(f'Erro ao buscar torneio: {e}', 'danger')
    
    return render_template('tournament/index.html')
@tournament_bp.route('/create', methods=['GET'])
def create():
    """
    Página de criação de torneios
    """
    return render_template('tournament/create.html', startups=Startup.query.all());

@tournament_bp.route('/create', methods=['POST'])
def create_tournament():
    try:
        startup_ids = request.form.getlist('startups[]')
        startups = [Startup.query.get(startup_id) for startup_id in startup_ids]        
        if not startups:
            flash('É necessário selecionar pelo menos 4 ou mais (4, 6, 8) startups.', 'danger')
            return redirect(url_for('tournament.create'));
        if len(startups) not in [4, 6, 8]:
            flash('Só é possível realizar torneios com 4, 6 ou 8 startups.', 'danger')
            return redirect(url_for('tournament.create'));
        
        #   Se já existe um torneio anterior, exclui-o
        db.session.query(Tournament).filter(Tournament.status == 'in_progress').delete();
        db.session.commit();
        
        tournament = Tournament(startups=startups)
        db.session.add(tournament);
        db.session.commit();
            
    except Exception as e:
        flash(f'Erro ao criar torneio: {e} = {e.args} = {type(e)}', 'danger')
        
    return redirect(url_for('tournament.index'));

#   Inserção de batalha no torneio
@tournament_bp.route('/add_battle/<int:tournament_id>/<int:startup_a_id>/<int:startup_b_id>', methods=['POST'])
def add_battle(tournament_id: int, startup_a_id: int, startup_b_id: int):
    try:
        battle = Battle(tournament_id, 1, startup_a_id, startup_b_id, 'in_progress')
        db.session.add(battle)
        db.session.commit()
        flash('Batalha adicionada ao torneio com sucesso!', 'success')
        return redirect(url_for('tournament.index'))
    except Exception as e:
        flash(f'Erro ao adicionar batalha ao torneio: {e}', 'danger')
    return redirect(url_for('tournament.index'));


#   Adiciona uma startup selecionada a um torneio
@tournament_bp.route('/add_startups', methods=['POST'])
def add_startups():
    try:
        startups = request.form.getlist('startups[]')
        tournament = Tournament.query.first()
        for startup_id in startups:
            startup = Startup.query.get(startup_id)
            tournament.battles.append(Battle(startup=startup))
        db.session.commit()
        flash('Startups adicionadas ao torneio com sucesso!', 'success')
        return redirect(url_for('tournament.index'))
    except Exception as e:
        flash(f'Erro ao adicionar startups ao torneio: {e}', 'danger')
        return redirect(url_for('tournament.index'))

@tournament_bp.route('/reset', methods=['POST'])
def reset():
    try:
        #   Delete todas as batalhas associadas ao torneio
        tournament = db.session.query(Tournament).first();
        for battle in tournament.battles:
            db.session.delete(battle);
        
        #   Delete o torneio
        db.session.delete(tournament);
        db.session.commit();
        
        flash('Torneio resetado com sucesso!', 'success')
        return redirect(url_for('tournament.index'))
    except Exception as e:
        flash(f'Erro ao resetar torneio: {e}', 'danger')
        return redirect(url_for('tournament.index'))

from app.routes.battle_routes import run_battle
from flask import Response

@tournament_bp.route('/run_all_battles', methods=['POST'])
def run_all_battles() -> Response:
    for battle in Battle.query.all():
        try:
            run_battle(battle.id)
        except Exception as e:
            flash(f"Erro ao executar a batalha {battle.id}: {e}", "danger")
            continue;

    flash("Batalhas executadas com sucesso!", "success");
    return redirect(url_for('tournament.index'));

@tournament_bp.route('/next_round', methods=['POST', 'GET'])
def next_round():
    try:
        #   Todas as batalhas deste round terminaram?
        if not Tournament.query.first().chk_round():
            flash("Todas as batalhas deste round ainda não foram concluidas!", "danger");
            return redirect(url_for('tournament.index'));
        
        with app.app_context():
            tournament : Tournament = db.session.query(Tournament).first();
            startups = tournament.round_winners();
            tournament.next_round(startups);
            db.session.commit();
            return redirect(url_for('tournament.index'));
    except Exception as e:
        flash(f"Erro ao executar o round: {e}", "danger");
        return redirect(url_for('tournament.index'));