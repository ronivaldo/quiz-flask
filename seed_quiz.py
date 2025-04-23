import requests
import json
import sys
from typing import Dict, Any, List

def load_config(path: str) -> Dict[str, Any]:
    """Load JSON configuration from a file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_or_create_materia(base_url: str, materia_name: str) -> int:
    """Return existing Materia ID or create it."""
    resp = requests.get(f"{base_url}/api/materias/")
    resp.raise_for_status()
    for m in resp.json():
        if m['nome'] == materia_name:
            print(f"Matéria encontrada: {materia_name} (ID: {m['id']})")
            return m['id']
    resp = requests.post(f"{base_url}/api/materias/", json={'nome': materia_name})
    resp.raise_for_status()
    m = resp.json()
    print(f"Matéria criada: {materia_name} (ID: {m['id']})")
    return m['id']

def get_or_create_quiz(base_url: str, quiz_title: str, materia_id: int) -> int:
    """Return existing Quiz ID or create it under the given Materia."""
    resp = requests.get(f"{base_url}/api/materias/{materia_id}/quizzes")
    resp.raise_for_status()
    for q in resp.json():
        if q['titulo'] == quiz_title:
            print(f"Quiz encontrado: {quiz_title} (ID: {q['id']})")
            return q['id']
    resp = requests.post(f"{base_url}/api/quizzes/", json={
        'titulo': quiz_title,
        'materia_id': materia_id
    })
    resp.raise_for_status()
    q = resp.json()
    print(f"Quiz criado: {quiz_title} (ID: {q['id']})")
    return q['id']

def get_existing_questions(base_url: str, quiz_id: int) -> List[str]:
    """Return list of existing question texts for a quiz."""
    resp = requests.get(f"{base_url}/api/quizzes/{quiz_id}/perguntas")
    resp.raise_for_status()
    return [p['pergunta'] for p in resp.json()]

def create_question(base_url: str, quiz_id: int, question: Dict[str, Any]) -> None:
    """Create a new question in the quiz."""
    payload = {
        'pergunta': question['pergunta'],
        'respostas': question['respostas'],
        'correta': question['correta'],
        'quiz_id': quiz_id
    }
    resp = requests.post(f"{base_url}/api/perguntas/", json=payload)
    resp.raise_for_status()
    print(f"Pergunta criada: {question['pergunta']}")

def seed_from_config(config_path: str, base_url: str = 'http://127.0.0.1:5000') -> None:
    """Read config JSON and seed the database via the API."""
    config = load_config(config_path)
    materia_name = config['materia']
    quiz_title = config['quiz']
    questions = config['perguntas']

    materia_id = get_or_create_materia(base_url, materia_name)
    quiz_id = get_or_create_quiz(base_url, quiz_title, materia_id)

    existing = get_existing_questions(base_url, quiz_id)
    print(f"{len(existing)} perguntas já existem no quiz.")

    for q in questions:
        if q['pergunta'] not in existing:
            create_question(base_url, quiz_id, q)
        else:
            print(f"Pergunta já existe: {q['pergunta']}")

    final = get_existing_questions(base_url, quiz_id)
    print(f"\nTotal de perguntas para '{quiz_title}': {len(final)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python seed_quiz.py <config.json>")
        sys.exit(1)
    seed_from_config(sys.argv[1])