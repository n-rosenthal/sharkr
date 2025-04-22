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
    #   Torneio terminado: mostrar o vencedor e as batalhas
    try:
        tournament = db.session.query(Tournament).filter(Tournament.status == 'completed').first();
        if tournament:
            return render_template('tournament/index.html', current_tournament=tournament, battles=tournament.battles, tournament_winner=tournament.winner);
    except Exception as e:
        flash(f'Erro ao buscar torneio: {e}', 'danger')
    
    #   Torneio em andamento: mostrar apenas as batalhas
    try:
        tournament = db.session.query(Tournament).filter(Tournament.status == 'in_progress').first();
        if tournament:
            with app.app_context():
                tournament.next_round();
            return render_template('tournament/index.html', current_tournament=tournament, battles=tournament.battles);
    except Exception as e:
        flash(f'Erro ao buscar torneio: {e}', 'danger')
    
    return render_template('tournament/index.html');
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

@tournament_bp.route('/delete_all_battles', methods=['POST'])
def delete_all_battles():
    try:
        #   Deleta todas as batalhas
        try:
            battles = Battle.query.all()
            for battle in battles:
                db.session.delete(battle)
        except Exception as e:
            flash(f"Não há batalhas para deletar: {e}", "danger")
        
        #   Deleta o torneio
        try:
            db.session.delete(Tournament.query.first())
        except Exception as e:
            flash(f"Erro ao deletar o torneio: {e}", "danger")
            
        #   Deleta os eventos
        try:
            db.session.query(Event).delete()
        except Exception as e:
            flash(f"Erro ao deletar os eventos: {e}", "danger")
            
        db.session.commit()
        flash("Batalhas deletadas com sucesso!", "success")
        return redirect(url_for('tournament.index'))
    except Exception as e:
        flash(f"Erro ao deletar as batalhas: {e}", "danger")
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
        
        #   Extração do torneio
        tournament = db.session.query(Tournament).first();
        
        #   Próximo round
        tournament.current_round += 1;
        db.session.commit();
        
        #   Extrair batalhas da última rodada
        #   SELECT winner_id FROM battle WHERE round = self.current_round;
        round = tournament.current_round - 1;
        winners = db.session.query(Battle.winner_id).filter(Battle.round_number == round).all();
        
        
        #   Caso 6 jogadores iniciais:  3 batalhas no round 1, 1 batalha no round 2, 1 batalha no round 3.
        #                               só é um problema no round 3
        if tournament.current_round == 3 and len(winners) == 1 and tournament.is_completed() == False:
            round_1_winners_ids = db.session.query(Battle.winner_id).filter(Battle.round_number == 1).all();            round_2_winners_ids = winners;
            
            #   Extrai as duas startups que disputaram o round 2
            r2_a = db.session.query(Battle.startup_a_id).filter(Battle.round_number == 2).all();
            r2_b = db.session.query(Battle.startup_b_id).filter(Battle.round_number == 2).all();
            
            #   Seleciona (1) a startup que venceu o round 1 mas não jogou o 2, e (2) a startup que venceu o round 2
            r3_a = [x[0] for x in round_1_winners_ids if x[0] not in [y[0] for y in r2_a] and x[0] not in [y[0] for y in r2_b]][0];
            r3_b = winners[0][0];
            
            #   Busca as startups apontadas por estes ids
            st_a = Startup.query.filter(Startup.id == r3_a).first();
            st_b = Startup.query.filter(Startup.id == r3_b).first();
            
            #   Monta a última batalha
            battle = Battle(tournament.id, tournament.current_round, st_a.id, st_b.id, "not_started");
            db.session.add(battle);
            db.session.commit();
            return redirect(url_for('tournament.index'));
        
        
        #   Geração de batalhas para o próximo round
        if len(winners) != 1:
            flash("Gerando batalhas do próximo round...", "success");
            startups: list[Startup] = [];
            
            for winner in winners:
                startups.append(Startup.query.filter(Startup.id == winner.winner_id).first());
                            
            tournament.generate_battles(startups);
            db.session.commit();
            return redirect(url_for('tournament.index'));
        #   Finaliza o torneio
        else:
            tournament.status = "finished";
            db.session.commit();
            flash("Torneio finalizado com sucesso!", "success");
            return redirect(url_for('reports.winner', winner_id=Startup.query.filter(Startup.id == winners[0].winner_id).first().id));
        
        return redirect(url_for('tournament.index'));
    except Exception as e:
        flash(f"Erro ao executar a batalha: {e}", "danger")
        return redirect(url_for('tournament.index'));