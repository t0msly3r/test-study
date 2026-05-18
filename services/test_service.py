import random
from models.question import Question
from models.subject import Subject


def get_questions_for_test(subject_id):
    questions = Question.get_by_subject(subject_id)
    random.shuffle(questions)
    return questions


def get_question_count(subject_id):
    return Subject.get_question_count(subject_id)