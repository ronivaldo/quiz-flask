from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Materia(db.Model):
    __tablename__ = 'materias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)
    quizzes = db.relationship('Quiz', backref='materia', cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(128), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)
    perguntas = db.relationship('Pergunta', backref='quiz', cascade='all, delete-orphan')

class Pergunta(db.Model):
    __tablename__ = 'perguntas'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String, nullable=False)
    respostas = db.Column(db.PickleType, nullable=False)
    correta = db.Column(db.String, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
