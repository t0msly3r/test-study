from models.subject import Subject


def create_subject(name):
    return Subject.create(name)


def list_subjects():
    return Subject.get_all()


def delete_subject(subject_id):
    Subject.delete(subject_id)


def get_subject_by_id(subject_id):
    subjects = Subject.get_all()
    for s in subjects:
        if s.id == subject_id:
            return s
    return None