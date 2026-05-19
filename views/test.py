import tkinter as tk
from tkinter import messagebox, ttk
from services.subject_service import list_subjects, get_subject_by_id
from services.test_service import get_questions_for_test
from models.question import Question


class TestView:
    def __init__(self, root, on_back):
        self.root = root
        self.on_back = on_back
        self.frame = tk.Frame(root)
        self.questions = []
        self.current_index = 0
        self.wrong_questions = []
        self.correct_count = 0
        self.wrong_count = 0

        title = tk.Label(
            self.frame, text="Hacer Test",
            font=("Helvetica", 20, "bold")
        )
        title.pack(pady=20)

        subject_frame = tk.Frame(self.frame)
        subject_frame.pack(pady=10)
        tk.Label(subject_frame, text="Asignatura:").pack(side="left")
        self.subject_combo = ttk.Combobox(subject_frame, state="readonly", width=30)
        self.subject_combo.pack(side="left", padx=5)
        tk.Button(subject_frame, text="Iniciar Test", command=self.start_test).pack(side="left", padx=5)

        self.content_frame = tk.Frame(self.frame)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=10)
        self.btn_retry = tk.Button(btn_frame, text="🔁 Repetir Fallos", command=self.retry_wrong, state="disabled")
        self.btn_retry.pack(side="left", padx=5)
        tk.Button(btn_frame, text="⬅️ Volver al menú", command=self.go_back).pack(side="left", padx=5)

        self.load_subjects()

    def load_subjects(self):
        subjects = list_subjects()
        self.subject_combo["values"] = [s.name for s in subjects]
        if subjects:
            self.subject_combo.current(0)

    def start_test(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        selected_name = self.subject_combo.get()
        subjects = list_subjects()
        subject_id = None
        for s in subjects:
            if s.name == selected_name:
                subject_id = s.id
                break

        if not subject_id:
            messagebox.showerror("Error", "Selecciona una asignatura.")
            return

        self.questions = get_questions_for_test(subject_id)
        if not self.questions:
            messagebox.showerror("Aviso", "No hay preguntas en esta asignatura.")
            return

        self.current_index = 0
        self.wrong_questions = []
        self.correct_count = 0
        self.wrong_count = 0
        self.btn_retry.config(state="disabled")

        self.show_question()

    def show_question(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if self.current_index >= len(self.questions):
            self.show_results()
            return

        q = self.questions[self.current_index]

        tk.Label(
            self.content_frame,
            text=f"Pregunta {self.current_index + 1}/{len(self.questions)}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        tk.Label(
            self.content_frame,
            text=q.text,
            font=("Helvetica", 12),
            wraplength=500,
            justify="center"
        ).pack(pady=10)

        self.selected_answer = tk.StringVar()

        for letter, text in [("A", q.option_a), ("B", q.option_b), ("C", q.option_c)]:
            tk.Radiobutton(
                self.content_frame,
                text=f"{letter}) {text}",
                variable=self.selected_answer,
                value=letter,
                font=("Helvetica", 11),
                anchor="w",
                wraplength=700,
                justify="left"
            ).pack(fill="x", padx=50, pady=4)

        btn_panel = tk.Frame(self.content_frame)
        btn_panel.pack(pady=15)

        self.btn_confirm = tk.Button(
            btn_panel, text="Confirmar", command=self.check_answer, width=12
        )
        self.btn_confirm.pack(side="left", padx=5)

        self.btn_next = tk.Button(
            btn_panel, text="Siguiente ➜", command=self.next_question, state="disabled", width=12
        )
        self.btn_next.pack(side="left", padx=5)

        tk.Button(
            btn_panel, text="Salir", command=self.exit_test, width=12
        ).pack(side="left", padx=5)

        self.feedback_label = tk.Label(self.content_frame, text="", font=("Helvetica", 11))
        self.feedback_label.pack()

    def check_answer(self):
        if not self.selected_answer.get():
            messagebox.showwarning("Aviso", "Selecciona una respuesta.")
            return

        q = self.questions[self.current_index]
        user_answer = self.selected_answer.get()

        if user_answer == q.correct_answer:
            self.correct_count += 1
            self.feedback_label.config(text="✅ ¡Correcto!", fg="green")
        else:
            self.wrong_questions.append(q)
            self.wrong_count += 1
            self.feedback_label.config(
                text=f"❌ Incorrecto. La respuesta era: {q.correct_answer}",
                fg="red"
            )

        self.btn_confirm.config(state="disabled")
        self.btn_next.config(state="normal")

    def next_question(self):
        self.current_index += 1
        self.show_question()

    def show_results(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        total = self.correct_count + self.wrong_count

        result_frame = tk.Frame(self.content_frame, bg="#ecf0f1", bd=2, relief="groove")
        result_frame.pack(pady=20, padx=40)

        tk.Label(
            result_frame,
            text="📊 RESULTADOS",
            font=("Helvetica", 18, "bold"),
            bg="#ecf0f1"
        ).pack(pady=10)

        tk.Label(
            result_frame,
            text=f"Total preguntas: {total}",
            font=("Helvetica", 12),
            bg="#ecf0f1"
        ).pack()

        tk.Label(
            result_frame,
            text=f"✅ Acertadas: {self.correct_count}",
            font=("Helvetica", 12),
            fg="green",
            bg="#ecf0f1"
        ).pack()

        tk.Label(
            result_frame,
            text=f"❌ Falladas: {self.wrong_count}",
            font=("Helvetica", 12),
            fg="red",
            bg="#ecf0f1"
        ).pack()

        pct = (self.correct_count / total * 100) if total > 0 else 0
        color = "#27ae60" if pct >= 70 else "#e74c3c" if pct < 50 else "#f39c12"
        tk.Label(
            result_frame,
            text=f"Nota: {pct:.0f}%",
            font=("Helvetica", 14, "bold"),
            fg=color,
            bg="#ecf0f1"
        ).pack(pady=10)

        if self.wrong_count > 0:
            self.btn_retry.config(state="normal")

    def retry_wrong(self):
        self.questions = self.wrong_questions[:]
        self.current_index = 0
        self.wrong_questions = []
        self.wrong_count = 0
        self.btn_retry.config(state="disabled")
        self.show_question()

    def exit_test(self):
        if self.current_index > 0 and (self.correct_count + self.wrong_count) < len(self.questions):
            if messagebox.askyesno("Salir", "¿Salir del test? No se guardará el progreso."):
                self.show_results()
        else:
            self.show_results()

    def go_back(self):
        self.frame.destroy()
        self.on_back()

    def show(self):
        self.frame.pack(fill="both", expand=True)