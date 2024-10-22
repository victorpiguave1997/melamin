from flask import Blueprint, render_template, request, send_from_directory, url_for, redirect, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager, db
import uuid
from  .model import Catalogo, db, Producto, Usuario, Rol
import os
from .config import Config
from flask_login import login_user, current_user, logout_user, login_required

view = Blueprint('view', __name__)

IMAGE_EXTENSION = {'jpg', 'jpeg'}

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def verify_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSION

@view.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        usuario_correo = request.form['usuario_correo']
        clave = request.form['clave']
        if not usuario_correo or not clave:
            flash('No se ingresaron los valores')
        usuario = Usuario.query.filter((Usuario.usuario==usuario_correo)| (Usuario.correo==usuario_correo)).first()
        if usuario:
            if check_password_hash(usuario.clave, clave):
                login_user(usuario)
            else:
                flash ('La contraseña es incorrecta')
        else:
            flash('El usuario no existe')
    return redirect(url_for('view.Panel'))

@view.route('/cerrar_sesion', methods=['GET', 'POST'])
def cerrar_cuenta():
    logout_user()
    return redirect(url_for('view.IndexPage'))

@view.route('/crear_cuenta', methods=['GET','POST'])
def crear_cuenta():
    if request.method == 'POST':
        nombre_usuario = request.form['usuario']
        correo = request.form['correo']
        clave = request.form['clave']
        if not nombre_usuario or not correo or not nombre_usuario:
            flash("Complete los campos")
        if Usuario.query.filter_by(usuario=nombre_usuario).first():
            flash('El usuario esta en uso')
        if Usuario.query.filter_by(correo=correo).first():
            flash ('El correo esta en uso')
        else:
            usuario = Usuario(usuario=nombre_usuario , correo=correo, clave=generate_password_hash(clave), rol_id = Rol.query.filter_by(rol="usuario").first().id)
            db.session.add(usuario)
            db.session.commit()
            login_user(usuario)
            return redirect(url_for('AdminPage'))
        return  redirect(url_for('view.IndexPage'))
    return render_template('auth/crear_cuenta.html')


@view.route('')
@view.route('/')
def IndexPage():
    return render_template('index.html')

@view.route('/panel', methods=['GET', 'POST'])
def Panel():
    catalogos = Catalogo.query.all()
    return render_template('/admin/index.html', catalogos=catalogos)

@view.route('/crate_catalogo', methods=['GET', 'POST'])
def CreateCatalogo():
    if request.method == 'POST':
        imagen = request.files['portada']
        titulo = request.form['titulo']
        detalle = request.form['detalle']
        secure_portada = secure_filename(imagen.filename)
        ext = secure_portada.rsplit('.', 1)[1].lower()
        new_portada = f'{uuid.uuid4()}.{ext}'
        imagen.save(os.path.join(Config.UPLOAD_FOLDER,new_portada))
        catalogo = Catalogo(titulo=titulo, detalle=detalle, portada=new_portada)
        db.session.add(catalogo)
        db.session.commit()
        print (new_portada)
        print (titulo)
        print (detalle)
    return redirect(url_for('view.AdminPage'))

@view.route('/eliminar_categoria/<int:id>')
@login_required
def DeleteCatalogo(id):
    if current_user.rol.rol != 'admin':
        flash('No se puede realizar esta operación')
        return redirect(url_for('view.Panel'))
    else:
        catalogo = Catalogo.query.filter_by(id=id).first()
        if catalogo:
            db.session.delete(catalogo)
            db.session.commit()
            os.remove(os.path.join(Config.UPLOAD_FOLDER, catalogo.portada))
            flash('Elimación correcta')
        else:
            flash('No se encontro elemento')
            return redirect(url_for('view.Panel'))

@view.route('/detail_catalogo/<int:id>')
def DetailCatalogo(id):
    catalogo = Catalogo.query.filter_by(id=id).first()
    if catalogo:
        return catalogo.titulo
    else:
        return "No existe"

@view.route('/update_catalogo/<int:id>', methods=['GET', 'POST'])
def UpdateCatalogo(id):
    catalogo = Catalogo.query.filter_by(id=id).first()
    if catalogo:
        if request.method == 'POST':
            return "cambios realizados"
        else:
            print (catalogo)
            return render_template('index.html', catalogo=catalogo)
    else:
        return "No existe te regresaremos al inicio"
    
@view.route('/agregar_producto', methods=['GET','POST'])
def agregar_producto():
    if request.method == 'POST':
        titulo = request.form['titulo']
        detalle = request.form['detalle']
        catalogo = request.form['catalogo_id']
        portada = request.files['portada']
        secure_portada = secure_filename(portada.filename)
        ext = secure_portada.rsplit('.', 1)[1].lower()
        new_portada = f'{uuid.uuid4()}.{ext}'
        portada.save(os.path.join(Config.UPLOAD_FOLDER,new_portada))
        producto = Producto(titulo=titulo, detalle=detalle, catalogo_id=catalogo, portada=new_portada)
        db.session.add(producto)
        db.session.commit()

    return redirect(url_for('view.Panel'))

@view.route('/productos')
def productos():
    catalogos = Catalogo.query.all()
    productos = Producto.query.order_by(db.func.random()).all()
    return render_template('catalogo.html', catalogos=catalogos, productos=productos)


@view.route('/upload/<filename>')
def upload_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER,filename)

@view.route('/producto/update')
def update_producto(id):
    return render_template('/producto/update.html')