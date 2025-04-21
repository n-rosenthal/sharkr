import random
from itertools import combinations;

from app.extensions import db

from app.models.startup import Startup, Event
from flask import flash, redirect, render_template, url_for
from sqlalchemy import and_, or_, func as sql_func

class Battle(db.Model):
    """``Battle``
    Representação de uma batalha entre duas ``Startup``.
    
    Uma batalha é definida a partir de um torneio (`tournament_id`), do round neste torneio (`round_number`), das duas startups (`startup_a_id` e `startup_b_id`). Toda batalha possui um status (`status`), e um vencedor (``startup_id``, nulo, se o status da batalha não for `completed`).
    
    Methods:
    --------
    -   `run_battle()`
        Executa uma batalha. Se necessário, chama `shark()` para decidir a batalha.
        -   `shark()`
            Decide o vencedor da batalha em caso de empate, adicionando +2 pontos a um jogador aleatoriamente.
    -   `render()`
        Retorna o template da batalha. (``/templates/battles/card.html``)
    """
    __tablename__ = 'battle'
    id              = db.Column(db.Integer, primary_key=True)
    tournament_id   = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    round_number    = db.Column(db.Integer, nullable=False)
    startup_a_id    = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    startup_b_id    = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=False)
    status          = db.Column(db.String(20), nullable=False)
    winner_id       = db.Column(db.Integer, db.ForeignKey('startup.id'), nullable=True)
    
    def __init__(self, tournament_id, round_number, startup_a_id, startup_b_id, status):
        """
        Construtor para objetos ``Battle``.
        
        Parameters
        ----------
        tournament_id : int
            O id do torneio.
            
        round_number : int
            O round inicial do torneio.
            
        startup_a_id : int
            O id da primeira startup.
            
        startup_b_id : int
            O id da segunda startup.
            
        status : str
            O status da batalha, um de "not_started", "started" ou "completed".
        """
        self.tournament_id   = tournament_id;
        self.round_number    = round_number;
        self.startup_a_id    = startup_a_id;
        self.startup_b_id    = startup_b_id;
        self.status          = status;
        self.winner_id       = None;
        
    def __repr__(self):
        return f'<Battle {self.id}>'
    
    
    def run_battle(self):
        """Executa uma batalha. Se necessário, chama `shark()` para decidir a batalha."""
        if self.status != 'not_started':
            flash("Uma batalha não pode ser reexecutada.", "warning")
            return False
        self.status = 'started'
        db.session.commit();
        
        #   Extrai as batalhas a partir dos seus ids
        #   SELECT * FROM startups WHERE id = startup_a_id OR id = startup_b_id
        startup_a = Startup.query.get(self.startup_a_id)
        startup_b = Startup.query.get(self.startup_b_id)
        
        #   Decide o vencedor da batalha
        if startup_a.get_points() > startup_b.get_points():
            self.winner_id = startup_a.id
        elif startup_a.get_points() < startup_b.get_points():
            self.winner_id = startup_b.id
        else:
            #   Shark
            s = random.choice([startup_a, startup_b])
            self.winner_id = s.id
        
        self.status = 'completed';
        db.session.commit();
        return True
    
    def shark(self):
        """
        Desempata uma batalha adicionando aleatoriamente +2 pontos a um dos participantes.
        """
        if self.status != 'started':
            flash("Não existe desempate shark para batalhas não iniciadas.", "warning")
            return False;
        winner = Startup.query.get(random.choice([self.startup_a_id, self.startup_b_id]))
        winner.points += 2;
        
        self.status = 'completed';
        self.winner_id = winner.id;
        
        db.session.commit();
        
    def render(self):
        return render_template('battles/card.html',
                               battle=self,
                               startup_a=Startup.query.get(self.startup_a_id),
                               startup_b=Startup.query.get(self.startup_b_id),
                               events_a=Event.query.filter_by(startup_id=self.startup_a_id).all(),
                               events_b=Event.query.filter_by(startup_id=self.startup_b_id).all(),
                               )
        
    def winner(self) -> Startup:
        """
        Retorna o vencedor da batalha.
        
        Returns:
            Startup: o vencedor da batalha.
        """
        if(self.status != 'completed'):
            return None
        return Startup.query.get(self.winner_id);
        
tournament_rules: dict[int, tuple[int, list[int]]] = {
    4: (2, [2, 1]),
    6: (3, [3, 1, 1]),
    8: (3, [4, 2, 1]),
}

def delete_all_battles():
    db.session.query(Battle).delete();
    db.session.commit();

class Tournament(db.Model):
    """``Tournament``
    Representação de um torneio entre ``Startup``s.
    
    Um torneio é uma lista de batalhas entre startups.
    
    Attributes
    ----------
    id : int
        O id do torneio.
        
    name : str
        O nome do torneio.
        
    status : str
        O status do torneio, um de "not_started", "in_progress" ou "completed".
        
    current_round : int
        O round atual do torneio.
        
    startups : list[Startup]
        Uma lista de startups que participam do torneio.
    
    
    Methods
    -------
    __init__(self, startups: list[Startup] = [])
        Construtor para objetos ``Tournament``.
        
    __repr__(self)
        Retorna uma representação do torneio.
        
    first_round(self, startups: list[Startup])
        Cria o primeiro round do torneio.
        
    chk_round(self)
        Verifica se o round atual já terminou, portanto se é possível avançar para o próximo.
        
    next_round(self)
        Avança para o round seguinte do torneio.
        
    is_completed(self)
        Verifica se o torneio foi concluído.
        
    render(self)
        Retorna uma representação do torneio.
    """
    __tablename__ = 'tournament'
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(255), nullable=False)
    status          = db.Column(db.String(20), nullable=False)
    current_round   = db.Column(db.Integer, nullable=False)
    battles         = db.relationship('Battle', backref='tournament', lazy=True)

    def __init__(self, startups: list[Startup] = []):
        """
        Construtor para objetos ``Tournament``.
        """
        startups            = startups;
        self.status         = "not_started";
        self.current_round  = 0;
        self.battles        = [];
        self.name           = "Torneio de Startups";
        self.id             = 1;
        self.first_round(startups);
        
    def __repr__(self):
        return f'<Tournament {self.id}>'
    
    #   Torneio
    def first_round(self, startups: list[Startup]):
        """Verifica se o torneio recebeu uma quantidade aceitável de startups e, se sim, inicia o primeiro round.

        Parameters
        ----------
        startups : list[Startup]
            Uma lista de startups que participam do torneio.
        """
        
        if len(startups) not in tournament_rules:
            raise Exception("O torneio precisa de pelo menos 4 startups cadastradas para ser iniciado. São aceitos exclusivamente torneios de 4, 6 ou 8 startups.")
        
        self.status = "in_progress"
        self.current_round = 1
        self.battles = self.generate_battles(startups);
    
    def next_round(self):
        """
        Avança o torneio para o próximo nível, se for possível.
        """
        if(self.chk_round()):
            self.current_round += 1;
            self.battles = self.generate_battles(self.round_winners());
    
    #   Acessores
    def completed_battles(self) -> set[Battle]:
        """
        Retorna uma lista com as batalhas que foram concluídas.
        """
        return set([b for b in self.battles if b.is_completed()]);
    
    def current_round_battles(self) -> set[Battle]:
        """
        Retorna uma lista com as batalhas do round atual.
        """
        return set([b for b in self.battles if b.round_number == self.current_round]);
    
    #   Geradores
    def generate_battles(self, startups: list[Startup]) -> list[Battle]:
        """
        Retorna uma lista de batalhas para o round atual.
        
        Parameters
        ----------
        list[Startup]
            Uma lista de startups que participam do round.
            
        Returns
        -------
        list[Battle]
            Uma lista de batalhas para o round atual.
        """
        n_battles : int         = self.get_nbattles_round(self.get_n_initial_players(), self.current_round);
        battles : list[Battle]  = [];
        
        if self.current_round == 1:
            winners = startups;
        else:
            winners : list[Startup] = self.round_winners();
        
        #   `n_battles` par e não múltiplo de 3
        if n_battles % 2 == 0 and n_battles % 3 != 0:
            for _ in range(n_battles):
                try:
                    a = random.choice(winners);
                    b = random.choice(winners);
                    
                    winners.remove(a);
                    winners.remove(b);
                    
                    battles.append(Battle(tournament_id=self.id, round_number=self.current_round, startup_a_id=a.id, startup_b_id=b.id, status="in_progress"));
                    db.session.add(battles[-1]);
                    
                except:
                    break;
        #   `n_battles` par e múltiplo de 3 (#6)
        elif n_battles % 2 == 0 and n_battles % 3 == 0:
            for _ in range(n_battles):
                try:
                    a = random.choice(winners);
                    b = random.choice(winners);
                    
                    winners.remove(a);
                    winners.remove(b);
                    
                    battles.append(Battle(tournament_id=self.id, round_number=self.current_round, startup_a_id=a.id, startup_b_id=b.id, status="in_progress"));
                    db.session.add(battles[-1]);
                except:
                    break;
            
            #   Startup que sobrou
            if (len(winners) == 1):
                s = winners[0];
                s.win_battle();
                winners.remove(s);
            
        db.session.commit();
        return battles;
      
    
    #   Verificadores
    def chk_round(self) -> bool:
        """
        Retorna verdadeiro se todas as batalhas do round atual foram concluídas.
        É equivalente a pesquisar se existem `n` batalhas completas para o round atual, dado `n` como o número esperado de batalhas para (n_initial_players, current_round).
        
        Returns:
            bool: Verdadeiro se todas as batalhas do round atual foram concluídas.
        """
        return len(self.current_round_battles()) == tournament_rules[len(self.get_n_initial_players())][1][self.current_round - 1];
    
    def is_completed(self) -> bool:
        """
        Retorna verdadeiro se o torneio foi concluído.
        
        Returns:
            bool: Verdadeiro se o torneio foi concluído.
        """
        return self.status == "completed";
    
    
    #   Métodos Auxiliares
    def round_winners(self) -> list[Startup]:
        """
        Retorna uma lista com os startups que venceram o round atual.

        Returns:
            list[Startup]: lista de vencedores do round atual
        """
        return [b.winner() for b in self.current_round_battles()];
    
    def get_n_initial_players(self) -> int:
        """
        Retorna o número de players iniciais.
        
        Returns
        -------
        int
            O número de players iniciais.
        """
        #   Equivalente a extrair o primeiro round do torneio
        #   SELECT count(DISTINCT startup_id) FROM battle WHERE tournament_id = self.id AND round_number = 1;
        n_battles = db.session.query(Battle).filter(Battle.tournament_id == self.id).filter(Battle.round_number == 1).count();
        
        return (n_battles * 2);
        
    def get_nbattles_round(self, n_initial_players: int, curr_round: int) -> int:
        """
        Retorna o número de batalhas esperadas para o número de players iniciais e o round atual.
        
        Parameters
        ----------
        n_initial_players : int
            O número de players iniciais.
            
        curr_round : int
            O round atual.
            
        Returns
        -------
        int
            O número de batalhas esperadas.
        """
        return tournament_rules[n_initial_players][1][curr_round - 1];