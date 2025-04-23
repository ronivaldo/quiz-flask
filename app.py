from flask import Flask, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields
from models import db, Materia, Quiz, Pergunta
import os


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///quiz.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# create db
with app.app_context():
    db.create_all()

api = Api(app,
          version='1.0',
          title='Quiz API',
          description='API para gerenciamento de matérias, quizzes e perguntas',
          doc='/docs',
          prefix='/api')

ns_materias = api.namespace('materias', description='Operações sobre matérias', path='/materias')
ns_quizzes = api.namespace('quizzes', description='Operações sobre quizzes', path='/quizzes')
ns_perguntas = api.namespace('perguntas', description='Operações sobre perguntas', path='/perguntas')

materia_model = api.model('Materia', {
    'id': fields.Integer(readonly=True, description='ID'),
    'nome': fields.String(required=True, description='Nome da matéria')
})

quiz_model = api.model('Quiz', {
    'id': fields.Integer(readonly=True, description='ID'),
    'titulo': fields.String(required=True, description='Título do quiz'),
    'materia_id': fields.Integer(required=True, description='ID da matéria')
})

pergunta_model = api.model('Pergunta', {
    'id': fields.Integer(readonly=True, description='ID'),
    'pergunta': fields.String(required=True, attribute='texto', description='Texto da pergunta'),
    'respostas': fields.List(fields.String, required=True, description='Opções de resposta'),
    'correta': fields.String(required=True, description='Resposta correta'),
    'quiz_id': fields.Integer(required=True, description='ID do quiz')
})

@ns_materias.route('/')
class MateriaList(Resource):
    @ns_materias.marshal_list_with(materia_model)
    def get(self):
        return Materia.query.all()

    @ns_materias.expect(materia_model)
    @ns_materias.marshal_with(materia_model, code=201)
    def post(self):
        data = api.payload
        m = Materia(nome=data['nome'])
        db.session.add(m)
        db.session.commit()
        return m, 201

@ns_materias.route('/<int:id>')
@ns_materias.response(404, 'Matéria não encontrada')
@ns_materias.param('id', 'ID da matéria')
class MateriaResource(Resource):
    @ns_materias.marshal_with(materia_model)
    def get(self, id):
        return Materia.query.get_or_404(id)

    @ns_materias.expect(materia_model)
    @ns_materias.marshal_with(materia_model)
    def put(self, id):
        m = Materia.query.get_or_404(id)
        m.nome = api.payload['nome']
        db.session.commit()
        return m

    @ns_materias.response(204, 'Matéria deletada')
    def delete(self, id):
        m = Materia.query.get_or_404(id)
        db.session.delete(m)
        db.session.commit()
        return '', 204

@ns_materias.route('/<int:id>/quizzes')
@ns_materias.response(404, 'Matéria não encontrada')
class MateriaQuizzes(Resource):
    @ns_materias.marshal_list_with(quiz_model)
    def get(self, id):
        materia = Materia.query.get_or_404(id)
        return materia.quizzes

@ns_quizzes.route('/')
class QuizList(Resource):
    @ns_quizzes.marshal_list_with(quiz_model)
    def get(self):
        return Quiz.query.all()

    @ns_quizzes.expect(quiz_model)
    @ns_quizzes.marshal_with(quiz_model, code=201)
    def post(self):
        data = api.payload
        q = Quiz(titulo=data['titulo'], materia_id=data['materia_id'])
        db.session.add(q)
        db.session.commit()
        return q, 201

@ns_quizzes.route('/<int:id>')
@ns_quizzes.response(404, 'Quiz não encontrado')
@ns_quizzes.param('id', 'ID do quiz')
class QuizResource(Resource):
    @ns_quizzes.marshal_with(quiz_model)
    def get(self, id):
        return Quiz.query.get_or_404(id)

    @ns_quizzes.expect(quiz_model)
    @ns_quizzes.marshal_with(quiz_model)
    def put(self, id):
        q = Quiz.query.get_or_404(id)
        data = api.payload
        q.titulo = data['titulo']
        q.materia_id = data['materia_id']
        db.session.commit()
        return q

    @ns_quizzes.response(204, 'Quiz deletado')
    def delete(self, id):
        q = Quiz.query.get_or_404(id)
        db.session.delete(q)
        db.session.commit()
        return '', 204

@ns_quizzes.route('/<int:id>/perguntas')
@ns_quizzes.response(404, 'Quiz não encontrado')
class QuizPerguntas(Resource):
    @ns_quizzes.marshal_list_with(pergunta_model)
    def get(self, id):
        quiz = Quiz.query.get_or_404(id)
        return quiz.perguntas

@ns_perguntas.route('/')
class PerguntaList(Resource):
    @ns_perguntas.marshal_list_with(pergunta_model)
    def get(self):
        return Pergunta.query.all()

    @ns_perguntas.expect(pergunta_model)
    @ns_perguntas.marshal_with(pergunta_model, code=201)
    def post(self):
        data = api.payload
        p = Pergunta(texto=data['pergunta'], respostas=data['respostas'], correta=data['correta'], quiz_id=data['quiz_id'])
        db.session.add(p)
        db.session.commit()
        return p, 201

@ns_perguntas.route('/<int:id>')
@ns_perguntas.response(404, 'Pergunta não encontrada')
@ns_perguntas.param('id', 'ID da pergunta')
class PerguntaResource(Resource):
    @ns_perguntas.marshal_with(pergunta_model)
    def get(self, id):
        return Pergunta.query.get_or_404(id)

    @ns_perguntas.expect(pergunta_model)
    @ns_perguntas.marshal_with(pergunta_model)
    def put(self, id):
        p = Pergunta.query.get_or_404(id)
        data = api.payload
        p.texto = data['pergunta']
        p.respostas = data['respostas']
        p.correta = data['correta']
        p.quiz_id = data['quiz_id']
        db.session.commit()
        return p

    @ns_perguntas.response(204, 'Pergunta deletada')
    def delete(self, id):
        p = Pergunta.query.get_or_404(id)
        db.session.delete(p)
        db.session.commit()
        return '', 204

@app.route('/')
def index():
    materias = Materia.query.all()
    return render_template('index.html', materias=materias)

@app.route('/materia/<int:mid>')
def lista_quizzes(mid):
    materia = Materia.query.get_or_404(mid)
    return render_template('quizzes.html', materia=materia)

@app.route('/materia/<int:mid>/quiz/<int:qid>')
def executa_quiz(mid, qid):
    quiz = Quiz.query.get_or_404(qid)
    return render_template('quiz.html', quiz=quiz)

if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)
