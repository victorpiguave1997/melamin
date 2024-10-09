from app import db

class Usuario (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(10), unique=True)
    correo = db.Column(db.String(120))
    clave = db.Column(db.String(120))

class Catalogo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo  = db.Column(db.String(50))
    detalle = db.Column(db.String(200))
    portada = db.Column(db.String(120))
    productos = db.relationship('Producto', backref='catalogo', lazy=True)

class Producto (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catalogo_id = db.Column(db.Integer, db.ForeignKey('catalogo.id'), nullable=False)
    titulo  = db.Column(db.String(50))
    detalle = db.Column(db.String(200))
    portada = db.Column(db.String(120))