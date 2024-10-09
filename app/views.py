from flask import Blueprint, render_template, request, current_app, send_from_directory, url_for, redirect
from werkzeug.utils import secure_filename
import uuid
from  .model import Catalogo, db, Producto
import os
from .config import Config

view = Blueprint('view', __name__)

IMAGE_EXTENSION = {'jpg', 'jpeg'}


def verify_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSION

@view.route('')
@view.route('/')
def IndexPage():
    return render_template('index.html')

@view.route('/dashboard', methods=['GET', 'POST'])
def AdminPage():
    catalogos = Catalogo.query.all()
    return render_template('/admin/index.html', catalogos=catalogos)

@view.route('/dashboard/catalogos')
def AdminCatalogo():
    catalogos = Catalogo.query.all()
    return render_template('admin/catalogos/index.html', catalogos=catalogos)


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

@view.route('/delete_catalogo/<int:id>')
def DeleteCatalogo(id):
    catalogo = Catalogo.query.filter_by(id=id).first()
    if catalogo:
        db.session.delete(catalogo)
        db.session.commit()
        return "Eliminación correcta"
    else:
        return 'fail'
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
    


@view.route('/crate_producto', methods=['GET','POST'])
def CreateProduct():
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

    return redirect(url_for('view.AdminPage'))


@view.route('/catalogo')
def CatalogoPage():
    catalogos = Catalogo.query.all()
    return render_template('catalogo.html', catalogos=catalogos)

@view.route('/productos')

@view.route('/upload/<filename>')
def upload_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER,filename)

@view.route('/producto/update')
def update_producto(id):
    return render_template('/producto/update.html')