from database.db import get_connection


class Subject:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM subjects ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        return [Subject(id=row["id"], name=row["name"]) for row in rows]

    @staticmethod
    def create(name):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    @staticmethod
    def delete(subject_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE subject_id = ?", (subject_id,))
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_question_count(subject_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions WHERE subject_id = ?", (subject_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count


