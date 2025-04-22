""" sharkr/app/extensions.py
Imports de extensões para Flask, SQLAlchemy.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#   Instância do banco de dados
db      = SQLAlchemy();

#   Instância do gerenciador de migrações
migrate = Migrate();