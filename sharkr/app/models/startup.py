"""
`app/models/startup.py`

"""

from app.extensions import db
from app.models.battle import Battle

from datetime import datetime

from flask import render_template

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
    
    def __init__(self, name, slogan, year):
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
        points += 30 * len(db.session.query(Battle).filter(Battle.winner_id == self.id).all());
        
        #   Pontos por eventos registrados
        events = db.session.query(Event).filter(Event.startup_id == self.id).all();
        for event in events:
            points += event.get_value();
            
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
    user_id         = db.Column(db.Integer, nullable=False);
    startup_id      = db.Column(db.Integer, nullable=False);
    event_type      = db.Column(db.String(20), nullable=False);
    battle_id       = db.Column(db.Integer, db.ForeignKey('battle.id'), nullable=False)
    
    def __init__(self, user_id, startup_id, event_type, battle_id):
        """
        Construtor para objetos `Event`
        
        Parameters
        ----------
        user_id : int
            O id do utilizador que registrou o evento.
            
        startup_id : int
            O id da startup que registrou o evento.
            
        event_type : str
            O tipo de evento, um de "pitch_convincente" | "produto_com_bugs" | "boa_tracao_usuarios" | "investidor_irritado" | "pitch_fake_news"
            
        battle_id : int
            O id da batalha em que o evento ocorreu.
        """
        self.user_id = user_id
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
            
