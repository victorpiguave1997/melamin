from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

executed = False

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app,db)
    
    from .views import view
    from .model import Usuario, Rol
    from werkzeug.security import generate_password_hash
    app.register_blueprint(view, url_prefix="/")

    with app.app_context():
         if not Rol.query.filter_by(rol='admin' ).first():
             rol_admin = Rol(rol = 'admin')
             rol_user = Rol(rol='usuario')
             db.session.add(rol_admin)
             db.session.add(rol_user)
             db.session.commit()

         if not Usuario.query.filter_by(usuario='admin').first():
             usuario = Usuario(
                 usuario='admin',
                 correo='admin@example.com',
                 clave= generate_password_hash('admin'),
                 rol_id = Rol.query.filter_by(rol="admin").first().id
             )
             db.session.add(usuario)
             db.session.commit()

    return app


