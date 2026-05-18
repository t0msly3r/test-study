import tkinter as tk
from tkinter import messagebox, ttk
from services.subject_service import list_subjects
from models.question import Question
import re


class QuestionsView:
    def __init__(self, root, on_back):
        self.root = root
        self.on_back = on_back
        self.frame = tk.Frame(root)
        self.question_rows = []
        self.parsed_questions = []
        self.subject_id = None

        title = tk.Label(
            self.frame, text="Añadir Preguntas",
            font=("Helvetica", 20, "bold")
        )
        title.pack(pady=20)

        subject_frame = tk.Frame(self.frame)
        subject_frame.pack(pady=5)
        tk.Label(subject_frame, text="Asignatura:").pack(side="left")
        self.subject_combo = ttk.Combobox(subject_frame, state="readonly", width=30)
        self.subject_combo.pack(side="left", padx=5)
        tk.Button(subject_frame, text="Ver preguntas", command=self.view_questions).pack(side="left", padx=5)

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=5)

        self.tab_manual = tk.Frame(self.notebook)
        self.tab_paste = tk.Frame(self.notebook)
        self.notebook.add(self.tab_manual, text="Entrada Manual")
        self.notebook.add(self.tab_paste, text="Pegar Texto")

        self.setup_manual_tab()
        self.setup_paste_tab()

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="💾 Guardar Preguntas", command=self.save_questions).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑️ Limpiar", command=self.clear_fields).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⬅️ Volver", command=self.go_back).pack(side="left", padx=5)

        self.load_subjects()

    def load_subjects(self):
        subjects = list_subjects()
        self.subject_combo["values"] = [s.name for s in subjects]
        if subjects:
            self.subject_combo.current(0)

    def get_subject_id(self):
        selected_name = self.subject_combo.get()
        subjects = list_subjects()
        for s in subjects:
            if s.name == selected_name:
                return s.id
        return None

    def setup_manual_tab(self):
        self.count_frame = tk.Frame(self.tab_manual)
        self.count_frame.pack(pady=5)
        tk.Label(self.count_frame, text="Nº de preguntas a añadir:").pack(side="left")
        self.count_entry = tk.Entry(self.count_frame, width=5)
        self.count_entry.insert(0, "3")
        self.count_entry.pack(side="left", padx=5)
        tk.Button(self.count_frame, text="Generar campos", command=self.generate_fields).pack(side="left")

        self.canvas_frame = tk.Frame(self.tab_manual)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def setup_paste_tab(self):
        top_frame = tk.Frame(self.tab_paste)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(
            top_frame,
            text="Formato: ¿pregunta? 1.respuesta 2.respuesta 3.respuesta;correcta",
            font=("Helvetica", 9)
        ).pack(side="left")
        tk.Button(top_frame, text="📋 Pegar desde portapapeles", command=self.paste_from_clipboard).pack(side="left", padx=10)

        self.paste_text = tk.Text(self.tab_paste, height=12, wrap="word", font=("Courier", 10))
        self.paste_text.pack(fill="both", expand=True, padx=10, pady=5)

        parse_btn_frame = tk.Frame(self.tab_paste)
        parse_btn_frame.pack(pady=5)
        tk.Button(parse_btn_frame, text="🔍 Analizar texto", command=self.parse_pasted_text).pack(side="left", padx=5)
        tk.Button(parse_btn_frame, text="🗑️ Limpiar", command=lambda: self.paste_text.delete("1.0", "end")).pack(side="left", padx=5)

        self.preview_frame = tk.Frame(self.tab_paste)
        self.preview_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.preview_label = tk.Label(self.preview_frame, text="Sin análisis", font=("Helvetica", 10))
        self.preview_label.pack()

        self.preview_canvas = tk.Canvas(self.preview_frame, height=200)
        self.preview_scroll = ttk.Scrollbar(self.preview_frame, orient="vertical", command=self.preview_canvas.yview)
        self.preview_inner = tk.Frame(self.preview_canvas)
        self.preview_inner.bind("<Configure>", lambda e: self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all")))
        self.preview_canvas.create_window((0, 0), window=self.preview_inner, anchor="nw")
        self.preview_canvas.configure(yscrollcommand=self.preview_scroll.set, state="disabled")

    def paste_from_clipboard(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.paste_text.delete("1.0", "end")
            self.paste_text.insert("1.0", clipboard_text)
        except tk.TclError:
            messagebox.showwarning("Aviso", "No hay texto en el portapapeles.")

    def parse_pasted_text(self):
        for widget in self.preview_inner.winfo_children():
            widget.destroy()
        self.parsed_questions = []

        text = self.paste_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Aviso", "No hay texto para analizar.")
            return

        subject_id = self.get_subject_id()
        if not subject_id:
            messagebox.showerror("Error", "Selecciona una asignatura.")
            return

        raw_questions = re.split(r';\s*', text)
        parsed = []
        errors = []

        for i, block in enumerate(raw_questions):
            block = block.strip()
            if not block:
                continue

            match = re.match(r'^(.+?)\?\s*(.+?)$', block)
            if not match:
                errors.append(f"Bloque {i+1}: no se encontró formato de pregunta")
                continue

            enunciado = match.group(1).strip() + "?"
            rest = match.group(2).strip()

            opts_match = re.findall(r'(\d)\.\s*(.+?)(?=\s+\d\.|$)', rest)
            if len(opts_match) < 3:
                errors.append(f"Bloque {i+1}: se esperaban 3 opciones")
                continue

            options = {int(num): opt.strip() for num, opt in opts_match}
            correct_letter = rest[-1].upper()
            if correct_letter not in ("A", "B", "C"):
                errors.append(f"Bloque {i+1}: respuesta correcta inválida '{correct_letter}'")
                continue

            q = {
                "text": enunciado,
                "a": options.get(1, ""),
                "b": options.get(2, ""),
                "c": options.get(3, ""),
                "correct": correct_letter,
                "subject_id": subject_id
            }
            parsed.append(q)

        self.parsed_questions = parsed

        summary = f"Detectadas: {len(parsed)} preguntas"
        if errors:
            summary += f" | Errores: {len(errors)}"
        self.preview_label.config(text=summary)

        if errors:
            error_text = "\n".join(errors[:10])
            if len(errors) > 10:
                error_text += f"\n... y {len(errors)-10} más"
            tk.Label(self.preview_inner, text=f"⚠️ {error_text}", fg="red", font=("Helvetica", 9), wraplength=600).pack(anchor="w", pady=2)

        for i, q in enumerate(parsed):
            color = "#27ae60" if q["correct"] == "A" else "#3498db" if q["correct"] == "B" else "#9b59b6"
            frame = tk.Frame(self.preview_inner, relief="groove", bd=1)
            frame.pack(fill="x", padx=5, pady=3)
            tk.Label(frame, text=f"{i+1}. {q['text']}", font=("Helvetica", 9, "bold"), wraplength=500, anchor="w").pack(anchor="w")
            for j, (letter, key) in enumerate([("A", "a"), ("B", "b"), ("C", "c")]):
                color_label = "green" if letter == q["correct"] else "gray"
                tk.Label(frame, text=f"  {letter}) {q[key]}", fg=color_label, font=("Helvetica", 9), anchor="w").pack(anchor="w")

        self.preview_canvas.configure(state="normal")

        self.question_rows = []
        for q in self.parsed_questions:
            self.question_rows.append({
                "text": q["text"],
                "a": q["a"],
                "b": q["b"],
                "c": q["c"],
                "correct": q["correct"]
            })

    def generate_fields(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        self.question_rows = []

        try:
            count = int(self.count_entry.get())
            if count < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Introduce un número válido.")
            return

        subject_id = self.get_subject_id()
        if not subject_id:
            messagebox.showerror("Error", "Selecciona una asignatura.")
            return

        canvas = tk.Canvas(self.canvas_frame, height=400)
        scrollbar = ttk.Scrollbar(self.canvas_frame, orient="vertical", command=canvas.yview)
        inner_frame = tk.Frame(canvas)

        inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i in range(count):
            row_frame = tk.LabelFrame(inner_frame, text=f"Pregunta {i + 1}", padx=10, pady=5)
            row_frame.pack(fill="x", padx=10, pady=5)

            tk.Label(row_frame, text="Enunciado:").grid(row=0, column=0, sticky="w")
            text_entry = tk.Entry(row_frame, width=60)
            text_entry.grid(row=0, column=1, pady=2)

            entries = [text_entry]
            for letter in ["A", "B", "C"]:
                tk.Label(row_frame, text=f"Opción {letter}:").grid(row=len(entries), column=0, sticky="w")
                e = tk.Entry(row_frame, width=60)
                e.grid(row=len(entries), column=1, pady=2)
                entries.append(e)

            tk.Label(row_frame, text="Correcta:").grid(row=len(entries), column=0, sticky="w")
            correct_combo = ttk.Combobox(row_frame, values=["A", "B", "C"], state="readonly", width=5)
            correct_combo.grid(row=len(entries), column=1, sticky="w", pady=2)
            entries.append(correct_combo)

            self.question_rows.append({
                "text": text_entry,
                "a": entries[1],
                "b": entries[2],
                "c": entries[3],
                "correct": correct_combo
            })

    def save_questions(self):
        subject_id = self.get_subject_id()
        if not subject_id:
            messagebox.showerror("Error", "Selecciona una asignatura válida.")
            return

        if not self.question_rows:
            messagebox.showwarning("Aviso", "No hay preguntas para guardar. Genera campos o analiza texto.")
            return

        questions_data = []
        errors = []

        for i, row in enumerate(self.question_rows):
            if isinstance(row["text"], tk.Widget):
                text = row["text"].get().strip()
                opt_a = row["a"].get().strip()
                opt_b = row["b"].get().strip()
                opt_c = row["c"].get().strip()
                correct = row["correct"].get().strip().upper()
            else:
                text = row["text"]
                opt_a = row["a"]
                opt_b = row["b"]
                opt_c = row["c"]
                correct = row["correct"]

            if not all([text, opt_a, opt_b, opt_c]):
                errors.append(f"Fila {i + 1}: completa todos los campos.")
                continue
            if correct not in ("A", "B", "C"):
                errors.append(f"Fila {i + 1}: respuesta correcta debe ser A, B o C.")
                continue

            questions_data.append((subject_id, text, opt_a, opt_b, opt_c, correct))

        if errors:
            messagebox.showerror("Errores en datos", "\n".join(errors))
            return

        Question.add_many(questions_data)
        messagebox.showinfo("Éxito", f"{len(questions_data)} preguntas guardadas.")
        self.clear_fields()

    def clear_fields(self):
        self.question_rows = []
        self.parsed_questions = []
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        for widget in self.preview_inner.winfo_children():
            widget.destroy()
        self.preview_label.config(text="Sin análisis")
        self.paste_text.delete("1.0", "end")
        self.preview_canvas.configure(state="disabled")

    def view_questions(self):
        subject_id = self.get_subject_id()
        if not subject_id:
            messagebox.showerror("Error", "Selecciona una asignatura.")
            return

        questions = Question.get_by_subject(subject_id)

        popup = tk.Toplevel(self.root)
        popup.title(f"Preguntas de {self.subject_combo.get()}")
        popup.geometry("700x400")

        frame = tk.Frame(popup)
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=("pregunta", "correcta"), show="headings")
        tree.heading("pregunta", text="Enunciado")
        tree.heading("correcta", text="Correcta")
        tree.column("pregunta", width=500)
        tree.column("correcta", width=100, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for q in questions:
            tree.insert("", "end", values=(q.text, q.correct_answer))

        if not questions:
            tk.Label(frame, text="No hay preguntas.").pack(pady=20)

        tk.Button(popup, text="Cerrar", command=popup.destroy).pack(pady=10)

    def go_back(self):
        self.frame.destroy()
        self.on_back()

    def show(self):
        self.frame.pack(fill="both", expand=True)