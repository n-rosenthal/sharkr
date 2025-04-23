import random;
import json;
from typing import Optional

from app.extensions import db

from flask import flash, redirect, render_template, url_for, current_app
from sqlalchemy import and_, or_, func as sql_func

#   Histórico
from app.models.history import BattleEntry;
from app import app;

class Startup(db.Model):
    """
    Representação de uma startup.
    
    
    Attributes
    ----------
    id : int
        O id da startup.
        
    name : str
        O nome da startup.
        
    slogan : str
        O slogan da startup.
        
    year : int
        O ano de fundação da startup.
        
    points : int = 70
        A pontuação da startup.
    """
    __tablename__ = 'startup'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True);
    name            = db.Column(db.String(255), nullable=False);
    slogan          = db.Column(db.String(255), nullable=False);
    year            = db.Column(db.Integer, nullable=False);
    points          = db.Column(db.Integer, nullable=False);
    
    def __init__(self, name: str, slogan: str, year: int) -> None:
        """
        Construtor para objetos `Startup`
        
        Parameters
        ----------
        name : str
            O nome da startup.
            
        slogan : str
            O slogan da startup.
            
        year : int
            O ano de fundação da startup.
        """
        self.name = name
        self.slogan = slogan
        self.year = year
        self.points = 70;

    def __repr__(self):
        return f'<Startup {self.name} ({self.points})>'
    
    def get_points(self) -> int:
        """
        Calcula a pontuação de uma `Startup` a partir dos eventos registrados sobre ela.

        Returns: int
            Pontuação atual da startup.
        """
        #   Pontuação inicial para todas as startups
        points:int = 70;
        
        #   +30 por round vencido
        #   Equivalente a contar quantas batalhas teve esta startup como vencedora
        #   SELECT count(battle_id) FROM battle WHERE winner_id = self.id;
        battle_points: int = 0
        try:
            b = db.session.query(Battle).filter(Battle.winner_id == self.id).count();
            battle_points = b * 30;
        except:
            pass;
        
        points += battle_points
        
        #   Pontos por eventos registrados
        event_points: int = 0;        
        try:
            e = db.session.query(Event).filter(Event.startup_id == self.id).all();
            for event in e:
                event_points += event.get_value();
        except:
            e = 0;
        
        points += event_points;
        
            
        self.points = points;
        return points;
    
    def win_battle(self) -> None:
        """
        Incrementa a pontuação de uma startup em 30.

        Returns:
            None
        """
        self.points += 30;
    
class Event(db.Model):
    """
    Eventos são objetos registrados à startups durante batalhas.
    
    Tipos:
    - pitch_convincente
    - produto_com_bugs
    - boa_tracao_usuarios
    - investidor_irritado
    - pitch_fake_news
    """
    __tablename__ = 'event'

    id              = db.Column(db.Integer, primary_key=True);
    startup_id      = db.Column(db.Integer, nullable=False);
    event_type      = db.Column(db.String(20), nullable=False);
    battle_id       = db.Column(db.Integer, db.ForeignKey('battle.id'), nullable=False)
    
    def __init__(self, startup_id, event_type, battle_id):
        """
        Construtor para objetos `Event`
        
        Parameters
        ----------            
        startup_id : int
            O id da startup que registrou o evento.
            
        event_type : str
            O tipo de evento, um de "pitch_convincente" | "produto_com_bugs" | "boa_tracao_usuarios" | "investidor_irritado" | "pitch_fake_news"
            
        battle_id : int
            O id da batalha em que o evento ocorreu.
        """
        self.startup_id = startup_id
        self.event_type = event_type
        self.battle_id = battle_id
        
    def __repr__(self):
        return f'<Event {self.id}>'
    
    def render(self) -> str:
        """
        Representação de um evento.
        """
        return render_template('startups/event_card.html', event=self);
    
    def get_value(self) -> int:
        """
        Retorna o valor de um evento.
        
        Returns:
            int: valor do evento
        """
        match self.event_type:
            case "pitch_convincente":
                return 6
            case "produto_com_bugs":
                return -4
            case "boa_tracao_usuarios":
                return 3
            case "investidor_irritado":
                return -6
            case "pitch_fake_news":
                return -8
            case _:
                return 0;
            
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'startup_id': self.startup_id,
            'event_type': self.event_type,
            'battle_id': self.battle_id
        }


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
    
    
    def run_battle(self) -> bool:
        """Executa uma batalha.
        
        Returns:
            bool: Verdadeiro se a batalha foi executada com sucesso, falso caso contrário.
        """
        #   Evita que uma batalha seja executada mais de uma vez
        if self.status != 'not_started':
            flash(f"A batalha {str(self)} não pôde ser executada agora, pois já foi executada anteriormente.", "warning");
            return False;

        #   Extrai as startups da batalha
        startup_a = db.session.get(Startup, self.startup_a_id);
        startup_b = db.session.get(Startup, self.startup_b_id);

        try:
            a_points, b_points = startup_a.get_points(), startup_b.get_points()
            if a_points > b_points:
                self.winner_id = startup_a.id;
            elif b_points > a_points:
                self.winner_id = startup_b.id;
            else:
                #   Se os pontos forem iguais, decide um vencedor aleatoriamente
                #   Regra do Shark: Se os pontos forem iguais, decide um vencedor aleatoriamente ao adicionar 2 pontos a sua pontuação.
                winner = random.choice([startup_a, startup_b]);
                winner.points += 2;
                self.winner_id = winner.id;

            #   Batalha termninada
            self.status = 'completed'
            db.session.commit();
            
            #   Registro do BattleEntry desta batalha
            events_a = json.dumps(
                [event.to_dict() for event in db.session.query(Event).filter(Event.startup_id == startup_a.id).all()]
            );
            
            events_b = json.dumps(
                [event.to_dict() for event in db.session.query(Event).filter(Event.startup_id == startup_b.id).all()]
            );
            
            #   Cria um objeto histórico da batalha
            history = BattleEntry(startup_a=db.session.query(Startup).get(self.startup_a_id).id,
                              startup_b=db.session.query(Startup).get(self.startup_b_id).id,
                              tournament_name=Tournament.query.get(self.tournament_id).name,
                              round_number=self.round_number,
                              winner=self.winner_id,
                              startup_a_points=a_points,
                              startup_b_points=b_points,
                              startup_a_events=events_a,
                              startup_b_events=events_b,
                              );
            
            db.session.add(history);
            db.session.commit();
            return True
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao executar batalha {str(self)}: {str(e)}", "danger")
            return False;
                
    def render(self):
        return render_template('battles/card.html',
                                battle=self,
                                startup_a=Startup.query.get(self.startup_a_id),
                                startup_b=Startup.query.get(self.startup_b_id),
                                events_a=Event.query.filter_by(startup_id=self.startup_a_id).all(),
                                events_b=Event.query.filter_by(startup_id=self.startup_b_id).all(),
                                );
    def winner(self) -> Startup:
        """
        Retorna o vencedor da batalha.
        
        Returns:
            Startup: o vencedor da batalha.
        """
        if(self.status != 'completed'):
            return None
        return Startup.query.get(self.winner_id);


def get_battle_points(startup_id: int) -> int:
    """
    Retorna a pontuação obtida por uma `Startup` ao vencer batalhas.
    
    Parameters
    ----------
    startup_id : int
        O id da startup.
        
    Returns
    -------
    int
        A pontuação atual da startup.
    """
    #   Equivalente a contar quantas batalhas teve esta startup como vencedora
    #   SELECT count(battle_id) FROM battle WHERE winner_id = self.id;
    b = db.session.query(Battle).filter(Battle.winner_id == startup_id).count();
    if(isinstance(b, int)): return 30*b;
    return 0;

def get_event_points(startup_id: int) -> int:
    """
    Retorna a pontuação adicionada a uma `Startup` após o registro de eventos.
    
    Parameters
    ----------
    startup_id : int
        O id da startup.
        
    Returns: int
        A pontuação atual da startup.
    """
    #   SELECT count(event_id) FROM event WHERE startup_id = self.id;
    e = db.session.query(Event).filter(Event.startup_id == startup_id).all();
    points = 0;
    
    for event in e:
        points += event.get_value();
        
    return points;
 
def delete_all_battles():
    db.session.query(Battle).delete();
    db.session.commit();

class Tournament(db.Model):
    """``Tournament``
    Representação de um torneio entre ``Startup``s.
    Um torneio é uma lista de batalhas entre startups.
    Somente é possível realizar torneios de 4, 6 ou 8 participantes.
    
    Estrutura do torneio:
    -   4 participantes: 2 rounds
        -   round 1 com 2 batalhas, round 2 com uma batalha final.
    -   6 participantes: 3 rounds
        -   round 1 com 3 batalhas, round 2 com 1 batalha entre vencedores do round 1. No round 3, o vencedor do round 1 que não disputou no round 2, irá enfrentar o vencedor do round 2.
    -   8 participantes: 3 rounds
        -   round 1 com 4 batalhas, round 2 com 2 batalhas entre vencedores do round 1. No round 3, o vencedor do round 1 que não disputou no round 2, irá enfrentar o vencedor do round 2.
    
    
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
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name            = db.Column(db.String(255), nullable=False)
    status          = db.Column(db.String(20), nullable=False)
    current_round   = db.Column(db.Integer, nullable=False)
    battles         = db.relationship('Battle', backref='tournament', lazy=True)

    def __init__(self):
        """
        Construtor para objetos ``Tournament``.
        """
        self.status         = "in_progress"
        self.current_round  = 0
        self.battles        = [];
        self.name           = "";
        
    def initialize(self, startups: list[Startup]) -> None:
        """
        Inicializa o torneio com as startups passadas como parâmetro.
        
        Parameters
        ----------
        startups : list[Startup]
            Lista de startups participantes do torneio.
        """
        with app.app_context():
            try:
                self.name = f"Torneio de Startups (#{self.id})";
                self.next_round(startups);
            except Exception as e:
                db.session.rollback();
                flash(f"Não conseguiu inicializar as batalhas do torneio: {e}");
                return;
            db.session.commit();
        
        
    def __repr__(self):
        return f'<Tournament {self.id}>'
        
    def next_round(self, startups: list[Startup]) -> None:
        """
        Avança o torneio para o próximo nível, se for possível.
        
        Parameters
        ----------
        startups : list[Startup]
            Lista de startups participantes do torneio **neste round**.
        """
        with app.app_context():
            #   Impossível avançar para o próximo round se já tterminou o torneio, ou se não existem competidores agora.
            if self.status == "completed" or not startups:
                flash(f"[1] Torneio concluido!", "warning");
                return;
            
            #   Ainda existem batalhasas neste round
            if not self.chk_round():
                flash(f"Round {self.current_round} ainda não acabou!", "warning");
                return;
            
            #   Vencedores do último round
            winners = [b.winner() for b in self.current_round_battles()];
            if not winners and self.current_round >= 3:
                #   Se o torneio acabou, finaliza o torneio
                self.status = "completed";
                db.session.commit();
                flash(f"[2] Torneio concluido!", "warning");
                return;
            
            #   Incrementa o round
            self.current_round += 1;
            
            #   Cria as batalhas para o round atual
            if self.current_round == 1:
                self._create_battles(startups);
            else:
                self._create_battles(winners);
            
            if len(winners) == 1:
                #   Se o torneio acabou, finaliza o torneio [2]
                self.status = "completed";
                db.session.commit();
                flash(f"[3] Torneio concluido!", "warning");
                return;
            
            #   Atualiza o torneio
            try:
                db.session.commit();
                flash(f"Avançou para o próximo round! Round {self.current_round} iniciado com sucesso!", "success");
            except Exception as e:
                db.session.rollback();
                flash(f"Erro crítico ao avançar para o próximo round: {e}", "danger");
                return;
        return;

    def _create_battles(self, startups: list[Startup]) -> None:
        """Cria batalhas para a lista de startups.
        
        Parameters
        ----------
        startups : list[Startup]
            Lista de startups participantes do torneio **neste round**.
        """
        while len(startups) >= 2:
            random.shuffle(startups)
            a = db.session.merge(startups.pop())  # Mescla na sessão atual
            b = db.session.merge(startups.pop())

            battle = Battle(
                tournament_id=self.id,
                round_number=self.current_round,
                startup_a_id=a.id,
                startup_b_id=b.id,
                status="not_started"
            )
            
            self.battles.append(battle)
            db.session.add(battle)

    def _handle_special_case(self, startups: list[Startup]) -> None:
        """Lida com o caso especial de 3 startups no round 2."""
        random.shuffle(startups)
        a = db.session.merge(startups.pop())
        b = db.session.merge(startups.pop())
        c = db.session.merge(startups.pop())

        battle = Battle(
            tournament_id=self.id,
            round_number=self.current_round,
            startup_a_id=a.id,
            startup_b_id=b.id,
            status="not_started"
        )
        
        self.battles.append(battle)
        db.session.add(battle)
        c.points += 30

        

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
        with current_app.app_context():
            if(self.status == "completed"):
                return [];
            
            #   dev 
            flash(str(len(startups)));
            
            match(len(startups)):
                case 2 | 3: n_battles = 1;
                case 4: n_battles = 2;
                case 6: n_battles = 3;
                case 8: n_battles = 4;
                case _: raise Exception("O torneio precisa de pelo menos 4 startups para prosseguir. Você pode gerenciar somente torneios de 4, 6 ou 8 startups.");
            
            if(len(startups) == 3):
                #   Seleciona a startup com mais pontos e avança para o próximo round
                startup_1 = max(startups, key=lambda s: s.points);
                startups.remove(startup_1);
                startup_1.win_battle();
                
                #   Monta uma batalha com as outras duas startups
                st_a, st_b = startups[0], startups[1];
                b = Battle(tournament_id=self.id,
                           round_number=self.current_round,
                           startup_a_id=st_a.id,
                           startup_b_id=st_b.id,
                           status="not_started");
                db.session.add(b);
                db.session.commit();
                return [b];
            else:
                while(startups):
                    if(len(startups) == 1): break;
                    random.shuffle(startups);
                    st_a, st_b = startups[0], startups[1];
                    startups.remove(st_a);
                    startups.remove(st_b);
                    b = Battle(tournament_id=self.id,
                               round_number=self.current_round,
                               startup_a_id=st_a.id,
                                startup_b_id=st_b.id,
                               status="not_started");
                    db.session.add(b);
                db.session.commit();
                return self.battles;
                
                
    
    #   Verificadores
    def chk_round(self) -> bool:
        """
        Retorna verdadeiro se todas as batalhas do round atual foram concluídas.
        É equivalente a pesquisar se existem `n` batalhas completas para o round atual, dado `n` como o número esperado de batalhas para (n_initial_players, current_round).
        
        Returns:
            bool: Verdadeiro se todas as batalhas do round atual foram concluídas.
        """
        #   batalhas deste round: select * from battle where tournament_id = self.id and round_number = self.current_round;
        b : list[Battle] = db.session.query(Battle).filter(Battle.tournament_id == self.id, Battle.round_number == self.current_round).all();
        
        for battle in b:
            if(not battle.status == "completed"):
                return False;
        return True;
    
    def get_winner(self) -> Optional[Startup]:
        """
        Se o torneio já estiver concluido, retorna a startup vencedora.
        
        Returns
        -------
        Startup
            A startup vencedora do torneio.
        """
        if self.is_completed():
            try:
                return self.battles[-1].winner();
            except:
                return None;
        return None;
    
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
    
    def get_n_initial_players(self) -> Optional[int]:
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
        
        #   Verifica se o número de batalhas é par
        if n_battles % 2 == 0:
            return n_battles * 2;
        else:
            raise ValueError("O número de batalhas do primeiro round deve ser par");
        
    def get_expected_battles(self, round_num: int) -> int:
        """
        Retorna o número de batalhas esperadas para dado round.
        
        Parameters
        ----------
        round_num : int
            O round para o qual se deseja saber o número de batalhas.
        
        Returns
        -------
        int
            O número de batalhas esperadas para dado round.
        """
        initial_players = len(self.battles) * 2;
        if initial_players == 6 and round_num == 2:
            return 1;
        return initial_players // (2 ** round_num);
    
    
    
    
    

