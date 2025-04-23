import random

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.models import Tournament, Startup, Battle, Event
from app import app


tournament_bp = Blueprint('tournament', __name__, url_prefix='/tournament')

#   Raiz do módulo de torneios
@tournament_bp.route('/', methods=['GET'])
def index():
    """
    Página de listagem de torneios
    
    current_tournament: Torneio em andamento
    battles: Batalhas do torneio em andamento
    tournament_winner: Vencedor do torneio
    """
    try:
        #   Extrai o último torneio criado
        current_tournament = Tournament.query.order_by(Tournament.id.desc()).first();
        
        #   Este torneio terminou?
        if current_tournament:
            try:
                if current_tournament.status == 'completed':
                    #   Busca o vencedor do torneio
                    tournament_winner = Startup.query.get(current_tournament.get_winner().id);
                    
                    #   Busca as batalhas do torneio
                    battles = Battle.query.filter(Battle.tournament_id == current_tournament.id).all();
                    
                    #   Busca os eventos das batalhas do torneio
                    events = Event.query.filter(Event.battle_id.in_([b.id for b in battles])).all();
                    
                    return render_template('tournament/index.html',
                                        current_tournament=current_tournament,
                                        battles=battles,
                                        tournament_winner=tournament_winner,
                                        events=events);
            except Exception as e:
                flash(f"Existe um torneio, mas não conseguiu extrair o vencedor: {e}", "danger");
                return render_template('tournament/index.html',
                                       current_tournament=current_tournament);
        
            #   Este torneio está em andamento?
            try:
                if current_tournament.status == 'in_progress':
                    #   Busca as batalhas do torneio
                    battles = Battle.query.filter(Battle.tournament_id == current_tournament.id).all();
                    
                    #   Filtra as batalhas, de modo que as batalhas em andamento estejam acima daquelas já completas
                    battles = [b for b in battles if b.status == 'not_started'] + [b for b in battles if b.status == 'completed'];
                    
                    #   Busca os eventos das batalhas do torneio
                    events = Event.query.filter(Event.battle_id.in_([b.id for b in battles])).all();
                    
                    #   Se todas as batalhas do round já houverem sido completas, então tenta avançar de round
                    if all([b.status != "not_started" for b in battles]):
                        return redirect(url_for('tournament.next_round'))
                    
                    return render_template('tournament/index.html',
                                        current_tournament=current_tournament,
                                        battles=battles,
                                        events=events);
            except Exception as e:
                flash(f"Existe um torneio, mas não conseguiu extrair as batalhas: {e}", "danger");
                return render_template('tournament/index.html');
        
        #   Não existe torneio em andamento
        else:
            return render_template('tournament/index.html');
    except Exception as e:
        flash(f"Não existe torneio em andamento: {e}", "danger");
        return render_template('tournament/index.html');
    return render_template('tournament/index.html')


#   Criação de um novo torneio, método GET
@tournament_bp.route('/create', methods=['GET'])
def create():
    """
    Página de criação de torneios
    """
    return render_template('tournament/create.html', startups=Startup.query.all());


#   Criação de um novo torneio
@tournament_bp.route('/create', methods=['POST'])
def create_tournament():
    try:
        # Extrai as startups selecionadas do formulário
        startup_ids = request.form.getlist('startups[]')
        startups = [Startup.query.get(startup_id) for startup_id in startup_ids]

        # Verifica se foram selecionadas startups
        if not startups:
            flash('É necessário selecionar pelo menos 4 ou mais (4, 6, 8) startups.', 'danger')
            return redirect(url_for('tournament.create'))

        # Verifica se foram selecionadas 4, 6 ou 8 startups
        if len(startups) not in [4, 6, 8]:
            flash('Só é possível realizar torneios com 4, 6 ou 8 startups.', 'danger')
            return redirect(url_for('tournament.create'))

        # Cria o torneio
        tournament = Tournament()
        tournament.initialize(startups);
        db.session.add(tournament)
        db.session.commit()
        
        flash(f'Torneio {tournament.id} criado com sucesso!', 'success')

    except Exception as e:
        flash(f'Erro ao criar torneio: {e}', 'danger')

    return redirect(url_for('tournament.index'))

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

#   Desenvolvimento, não usado na release
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

#   Desenvolvimento, não usado na release
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

#   Próximo round
@tournament_bp.route('/next_round', methods=['POST', 'GET'])
def next_round():
    try:
        tournament = db.session.query(Tournament).first()
        if not tournament:
            flash("Não há torneio criado.", "danger")
            return redirect(url_for('tournament.index'))

        # Check if current round is complete
        current_battles = Battle.query.filter_by(
            tournament_id=tournament.id,
            round_number=tournament.current_round
        ).all()
        
        if any(b.status != 'completed' for b in current_battles):
            flash("O torneio ainda possui batalhas em andamento.", "danger")
            return redirect(url_for('tournament.index'))

        #   Extrair os vencedores do round atual
        winners = []
        for battle in current_battles:
            if battle.winner_id:
                winner = Startup.query.get(battle.winner_id)
                winners.append(winner)
            else:
                flash("Ainda há batalhas em andamento.", "danger")
                return redirect(url_for('tournament.index'))

        #   Decidir as batalhas do próximo round
        if not winners:
            tournament.status = 'completed'
            db.session.commit()
            flash("Erro: torneio terminado sem vencedor", "warning")
            return redirect(url_for('tournament.index'))

        #   Incrementa round do torneio
        next_round_num = tournament.current_round + 1

        #   Caso especial, torneio com 6 participantes iniciais
        if len(winners) == 3 and next_round_num == 2:
            # Grant bye to highest-scoring winner
            s = max(winners, key=lambda x: x.points)
            winners.remove(s)
            s.points += 30
            db.session.add(s)

        #   Criar novas batalhas
        random.shuffle(winners)
        while len(winners) >= 2:
            battle = Battle(
                tournament_id=tournament.id,
                round_number=next_round_num,
                startup_a_id=winners.pop().id,
                startup_b_id=winners.pop().id,
                status='not_started'
            )
            db.session.add(battle)

        #   Atualizar estado do torneio
        tournament.current_round = next_round_num
        if len(winners) == 1:  # Final winner
            tournament.winner_id = winners[0].id
            tournament.status = 'completed'
            flash(f"Torneio terminado: {winners[0].name} vencedor.", "success")

        db.session.commit()
        return redirect(url_for('tournament.index'))

    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao chamar /next_round: {str(e)}", "danger")
        return redirect(url_for('tournament.index'))
