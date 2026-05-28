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

        self.btn_retry_during = None

        self.original_questions = None
        self.original_index = 0
        self.original_correct = 0
        self.original_wrong = []
        self.is_retry_mode = False

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
        if self.btn_retry_during:
            self.btn_retry_during.config(state="disabled")

        self.original_questions = None
        self.original_index = 0
        self.original_correct = 0
        self.original_wrong = []
        self.is_retry_mode = False

        self.show_question()

    def show_question(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if self.current_index >= len(self.questions):
            self.show_results()
            return

        q = self.questions[self.current_index]

        center_wrapper = tk.Frame(self.content_frame)
        center_wrapper.pack(expand=True, fill="both", padx=40)

        tk.Label(
            center_wrapper,
            text=f"Pregunta {self.current_index + 1}/{len(self.questions)}",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        tk.Label(
            center_wrapper,
            text=q.text,
            font=("Helvetica", 12),
            wraplength=700,
            justify="center"
        ).pack(pady=10)

        self.selected_answer = tk.StringVar()

        options_frame = tk.Frame(center_wrapper)
        options_frame.pack(pady=5)

        options = [("A", q.option_a), ("B", q.option_b), ("C", q.option_c)]
        if q.option_d:
            options.append(("D", q.option_d))
        for letter, text in options:
            tk.Radiobutton(
                options_frame,
                text=f"{letter}) {text}",
                variable=self.selected_answer,
                value=letter,
                font=("Helvetica", 11),
                anchor="w",
                wraplength=700,
                justify="left"
            ).pack(fill="x", pady=4)

        btn_panel = tk.Frame(center_wrapper)
        btn_panel.pack(pady=15)

        self.btn_confirm = tk.Button(
            btn_panel, text="Confirmar", command=self.check_answer, width=12
        )
        self.btn_confirm.pack(side="left", padx=5)

        self.btn_edit = tk.Button(
            btn_panel, text="✏️ Editar", command=self.edit_question, width=12
        )
        self.btn_edit.pack(side="left", padx=5)

        self.btn_next = tk.Button(
            btn_panel, text="Siguiente ➜", command=self.next_question, state="disabled", width=12
        )
        self.btn_next.pack(side="left", padx=5)

        self.btn_retry_during = tk.Button(
            btn_panel, text="🔁 Repetir Fallos", command=self.retry_wrong_during, state="disabled", width=12
        )
        self.btn_retry_during.pack(side="left", padx=5)

        tk.Button(
            btn_panel, text="Salir", command=self.exit_test, width=12
        ).pack(side="left", padx=5)

        self.feedback_label = tk.Label(self.content_frame, text="", font=("Helvetica", 11))
        self.feedback_label.pack()

        if self.wrong_questions and self.btn_retry_during:
            self.btn_retry_during.config(state="normal")
        elif self.btn_retry_during:
            self.btn_retry_during.config(state="disabled")

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
        result_frame.pack(pady=20, padx=40, expand=True)

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

        if self.is_retry_mode:
            retry_result_frame = tk.Frame(self.content_frame)
            retry_result_frame.pack(pady=15)

            tk.Button(retry_result_frame, text="▶️ Continuar examen", command=self.continue_original_test, width=18).pack(side="left", padx=5)
            tk.Button(retry_result_frame, text="⬅️ Volver al menú", command=self.go_back, width=18).pack(side="left", padx=5)
        else:
            if self.wrong_count > 0:
                self.btn_retry.config(state="normal")

    def retry_wrong_during(self):
        if not self.wrong_questions:
            messagebox.showwarning("Aviso", "No hay preguntas falladas aún.")
            return

        self.original_questions = self.questions[:]
        self.original_index = self.current_index
        self.original_correct = self.correct_count
        self.original_wrong = self.wrong_questions[:]
        self.is_retry_mode = True

        self.questions = self.wrong_questions[:]
        self.current_index = 0
        self.wrong_questions = []
        self.wrong_count = 0
        self.btn_retry_during.config(state="disabled")
        self.show_question()

    def continue_original_test(self):
        self.questions = self.original_questions[:]
        self.current_index = self.original_index
        self.correct_count = self.original_correct
        self.wrong_questions = self.original_wrong[:]
        self.wrong_count = len(self.wrong_questions)
        self.is_retry_mode = False

        self.original_questions = None
        self.original_index = 0
        self.original_correct = 0
        self.original_wrong = []

        self.show_question()

    def retry_wrong(self):
        self.original_questions = self.questions[:]
        self.original_index = 0
        self.original_correct = self.correct_count
        self.original_wrong = self.wrong_questions[:]
        self.is_retry_mode = True

        self.questions = self.wrong_questions[:]
        self.current_index = 0
        self.wrong_questions = []
        self.wrong_count = 0
        self.btn_retry.config(state="disabled")
        if self.btn_retry_during and self.btn_retry_during.winfo_exists():
            self.btn_retry_during.config(state="disabled")
        self.show_question()

    def exit_test(self):
        if self.current_index > 0 and (self.correct_count + self.wrong_count) < len(self.questions):
            if messagebox.askyesno("Salir", "¿Salir del test? No se guardará el progreso."):
                self.show_results()
        else:
            self.show_results()

    def edit_question(self):
        q = self.questions[self.current_index]

        popup = tk.Toplevel(self.root)
        popup.title("Editar Pregunta")
        popup.geometry("600x450")
        popup.resizable(False, False)

        tk.Label(popup, text="Editar Pregunta", font=("Helvetica", 16, "bold")).pack(pady=10)

        form_frame = tk.Frame(popup)
        form_frame.pack(fill="both", expand=True, padx=20, pady=5)

        tk.Label(form_frame, text="Enunciado:").grid(row=0, column=0, sticky="w", pady=5)
        text_entry = tk.Entry(form_frame, width=60)
        text_entry.grid(row=0, column=1, pady=5)
        text_entry.insert(0, q.text)

        opt_entries = {}
        letters = [("A", "option_a"), ("B", "option_b"), ("C", "option_c")]
        if q.option_d:
            letters.append(("D", "option_d"))
        for j, (letter, key) in enumerate(letters):
            tk.Label(form_frame, text=f"Opción {letter}:").grid(row=j + 1, column=0, sticky="w", pady=5)
            entry = tk.Entry(form_frame, width=60)
            entry.grid(row=j + 1, column=1, pady=5)
            entry.insert(0, getattr(q, key))
            opt_entries[key] = entry

        correct_values = [l for l, _ in letters]
        tk.Label(form_frame, text="Correcta:").grid(row=len(letters) + 1, column=0, sticky="w", pady=5)
        correct_combo = ttk.Combobox(form_frame, values=correct_values, state="readonly", width=5)
        correct_combo.grid(row=len(letters) + 1, column=1, sticky="w", pady=5)
        correct_combo.set(q.correct_answer)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=10)

        def save_edit():
            new_text = text_entry.get().strip()
            new_opts = {key: entry.get().strip() for key, entry in opt_entries.items()}
            new_correct = correct_combo.get()

            if not all([new_text, new_opts["option_a"], new_opts["option_b"], new_opts["option_c"]]):
                messagebox.showwarning("Aviso", "Completa todos los campos.")
                return
            if "option_d" in new_opts and not new_opts["option_d"]:
                messagebox.showwarning("Aviso", "Completa todos los campos.")
                return
            if new_correct not in ("A", "B", "C", "D"):
                messagebox.showwarning("Aviso", "Respuesta correcta debe ser A, B, C o D.")
                return

            Question.update(q.id, new_text, new_opts["option_a"], new_opts["option_b"], new_opts["option_c"], new_opts.get("option_d", ""), new_correct)

            q.text = new_text
            q.option_a = new_opts["option_a"]
            q.option_b = new_opts["option_b"]
            q.option_c = new_opts["option_c"]
            if "option_d" in new_opts:
                q.option_d = new_opts["option_d"]
            q.correct_answer = new_correct

            messagebox.showinfo("Éxito", "Pregunta actualizada.")
            popup.destroy()
            self.show_question()

        tk.Button(btn_frame, text="💾 Guardar", command=save_edit, width=12).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=popup.destroy, width=12).pack(side="left", padx=5)

    def go_back(self):
        self.frame.destroy()
        self.on_back()

    def show(self):
        self.frame.pack(fill="both", expand=True)