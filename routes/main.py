from flask import Blueprint, render_template
from utils import generate_csrf_token

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/survey')
def survey():
    from questions import get_gender_question, get_regular_questions
    gender_q = get_gender_question()
    regular_qs = get_regular_questions()
    return render_template('survey.html', gender_question=gender_q, questions=regular_qs, csrf_token=generate_csrf_token())

@main_bp.route('/results')
def results():
    return render_template('results.html', csrf_token=generate_csrf_token())

@main_bp.route('/about')
def about():
    return render_template('about.html')
