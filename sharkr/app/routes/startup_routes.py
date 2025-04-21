""" sharkr/app/routes/startup_routes.py
Rotas para criação, visualização e atualização de startups

@   '/startups'
"""

from flask              import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions     import db
from app.models.startup import Startup
from app.forms          import StartupForm

startup_bp = Blueprint('startup', __name__, url_prefix='/startups')

@startup_bp.route('/')
def index():
    """
    Índice de '/startups'
    """
    startups = Startup.query.all()
    return render_template('startups/index.html', startups=startups);


#   Criar uma startup
@startup_bp.route('/create', methods=['GET', 'POST'])
def create():
    """
    Criação de uma startup
    
    GET: Renderiza o template de criação de startup
    POST: Processa o formulário de criação de startup
    """
    #   GET: Renderiza o template de criação de startup
    if request.method == 'GET':
        return render_template('startups/create.html')
    
    #   POST: Processa o formulário de criação de startup
    if request.method == 'POST':
        name = request.form['name']
        slogan = request.form['slogan']
        year = request.form['year']

        startup = Startup(name=name, slogan=slogan, year=year)
        db.session.add(startup);
        db.session.commit();

        flash('Startup criada com sucesso!', 'success');
        return redirect(url_for('startup.index'));


#   Mostrar uma startup
@startup_bp.route('/<int:id>')
def show(id: int):
    """
    Rota para mostrar uma startup
    
    Parameters
    ----------
    id : int
        O id da startup.
    """
    startup = Startup.query.get_or_404(id)
    return render_template('startups/show.html', startup=startup)



#   Editar uma startup
@startup_bp.route('/<int:id>/update', methods=['GET', 'POST'])
def update(id: int):
    """
    Rota para atualizar uma startup
    
    Parameters
    ----------
    id : int
        O id da startup.
    """
    startup = Startup.query.get_or_404(id)
    if request.method == 'POST':
        startup.name = request.form['name']
        startup.slogan = request.form['slogan']
        startup.year = request.form['year']
        db.session.commit()
        flash('Startup atualizada com sucesso!', 'success')
        return redirect(url_for('startup.show', id=startup.id))
    return render_template('startups/update.html', startup=startup);



#   Deletar uma startup
@startup_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id: int):
    """
    Rota para deletar uma startup
    
    Parameters
    ----------
    id : int
        O id da startup.
    """
    startup = Startup.query.get_or_404(id)
    db.session.delete(startup)
    db.session.commit()
    flash('Startup deletada com sucesso!', 'success')
    return redirect(url_for('startup.index'))


#   Registrar um evento a uma startup
from app.models.startup import Event, get_value
@startup_bp.route('/<int:startup_id>/create_event/<string:event_type>', methods=['GET', 'POST'])
def create_event(startup_id: int, event_type: str):
    """
    Rota para registrar um evento a uma startup
    
    Parameters
    ----------
    startup_id : int
        O id da startup.
        
    event_type : str
        O tipo de evento, um de "pitch_convincente" | "produto_com_bugs" | "boa_tracao_usuarios" | "investidor_irritado" | "pitch_fake_news"
    """
    startup = Startup.query.get_or_404(startup_id)
    if request.method == 'POST':
        try:
            event = Event(user_id=1, startup_id=startup_id, event_type=event_type);
        except:
            event = Event(user_id=1, startup_id=startup_id, event_type=event_type, value=get_value(event_type));
            
        db.session.add(event)
        db.session.commit()
        
        #   Mostra mensagem de sucesso
        flash(f'Evento {event_type} registrado com sucesso!', 'success')
        
        #   Atualiza os pontos da startup
        from app.models.startup import get_points
        startup.points = get_points(startup_id);
        
        db.session.commit();
        
        #   Redireciona para a página de detalhes da startup
        return redirect(url_for('startup.index'));
        
    #   Refresh os pontos da startup
    startup.get_points();
    
    return redirect(url_for('startup.index', id=startup_id))

