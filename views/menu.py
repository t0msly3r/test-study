import tkinter as tk
from tkinter import messagebox


class MenuView:
    def __init__(self, root, on_subjects, on_add_questions, on_do_test):
        self.root = root
        self.on_subjects = on_subjects
        self.on_add_questions = on_add_questions
        self.on_do_test = on_do_test

        self.frame = tk.Frame(root, bg="#2c3e50")
        self.frame.pack(fill="both", expand=True)

        title = tk.Label(
            self.frame, text="📚 Study Tests",
            font=("Helvetica", 24, "bold"),
            bg="#2c3e50", fg="white"
        )
        title.pack(pady=40)

        buttons = [
            ("📖 Gestionar Asignaturas", self.on_subjects),
            ("➕ Añadir Preguntas", self.on_add_questions),
            ("✏️ Hacer Test", self.on_do_test),
        ]

        for text, cmd in buttons:
            btn = tk.Button(
                self.frame, text=text,
                font=("Helvetica", 14),
                width=25, height=2,
                command=cmd
            )
            btn.pack(pady=10)

        exit_btn = tk.Button(
            self.frame, text="❌ Salir",
            font=("Helvetica", 12),
            command=self.root.destroy
        )
        exit_btn.pack(pady=30)

    def destroy(self):
        self.frame.destroy()