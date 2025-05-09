""" sharkr/app/__init__.py
Inicialização do aplicativo, inicialização do banco de dados e configuração das rotas.
"""

#   Definição geral do aplicativo
from flask import Flask
from app.config import Config
from app.extensions import db, migrate

app = Flask(__name__)
app.config.from_object(Config)

#   Inicializa o banco de dados
db.init_app(app)
migrate.init_app(app, db)

#   Rotas
from flask import render_template, redirect, url_for, Blueprint
from app.routes.startup_routes      import startup_bp       #   Criação, visualização e atualização de startups
from app.routes.battle_routes       import battle_bp        #   Histórico de batalhas
from app.routes.tournament_routes   import tournament_bp    #   Gerencia e visualização de torneios
from app.routes.report_routes       import report_bp        #   Relatórios

#   Blueprint para página raiz
index_bp = Blueprint('index', __name__, url_prefix='/');

#   Redirecionamento da página raiz
@index_bp.route('/')
@index_bp.route('/index')
@index_bp.route('/logout')
def index():
    """sharkr\app\templates\root.html

    Returns:
        _type_: _description_
    """
    return render_template('root.html')

#   Rota para sair ("logout")

#   Registro das blueprint de rotas
app.register_blueprint(index_bp);
app.register_blueprint(startup_bp);
app.register_blueprint(battle_bp);
app.register_blueprint(tournament_bp);
app.register_blueprint(report_bp);

#   Cria todas as tabelas
with app.app_context():
    db.create_all()
    db.session.commit()