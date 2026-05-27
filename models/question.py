from database.db import get_connection


class Question:
    def __init__(self, id=None, subject_id=None, text=None,
                 option_a=None, option_b=None, option_c=None, option_d=None, correct_answer=None):
        self.id = id
        self.subject_id = subject_id
        self.text = text
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d
        self.correct_answer = correct_answer

    @staticmethod
    def get_by_subject(subject_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, subject_id, text, option_a, option_b, option_c, option_d, correct_answer
               FROM questions WHERE subject_id = ?""",
            (subject_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [Question(**dict(row)) for row in rows]

    @staticmethod
    def add_many(questions_data):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.executemany(
            """INSERT INTO questions (subject_id, text, option_a, option_b, option_c, option_d, correct_answer)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            questions_data
        )
        conn.commit()
        conn.close()

    @staticmethod
    def update(question_id, text, option_a, option_b, option_c, option_d, correct_answer):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE questions SET text=?, option_a=?, option_b=?, option_c=?, option_d=?, correct_answer=?
               WHERE id=?""",
            (text, option_a, option_b, option_c, option_d, correct_answer, question_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def delete(question_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        conn.close()