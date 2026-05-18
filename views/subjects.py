import tkinter as tk
from tkinter import messagebox, ttk
from services.subject_service import list_subjects, create_subject, delete_subject


class SubjectsView:
    def __init__(self, root, on_back):
        self.root = root
        self.on_back = on_back
        self.frame = tk.Frame(root)

        title = tk.Label(
            self.frame, text="Gestionar Asignaturas",
            font=("Helvetica", 20, "bold")
        )
        title.pack(pady=20)

        input_frame = tk.Frame(self.frame)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Nombre:").pack(side="left")
        self.name_entry = tk.Entry(input_frame, width=30)
        self.name_entry.pack(side="left", padx=5)
        tk.Button(input_frame, text="Crear", command=self.create_subject).pack(side="left")

        list_frame = tk.Frame(self.frame)
        list_frame.pack(fill="both", expand=True, pady=10, padx=20)

        self.tree = ttk.Treeview(list_frame, columns=("name", "questions"), show="headings")
        self.tree.heading("name", text="Asignatura")
        self.tree.heading("questions", text="Preguntas")
        self.tree.column("name", width=300)
        self.tree.column("questions", width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="🗑️ Eliminar", command=self.delete_selected).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🔄 Actualizar", command=self.refresh_list).pack(side="left", padx=5)
        tk.Button(btn_frame, text="⬅️ Volver", command=self.go_back).pack(side="left", padx=5)

        self.refresh_list()

    def create_subject(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Aviso", "Introduce un nombre.")
            return
        if create_subject(name):
            self.name_entry.delete(0, tk.END)
            self.refresh_list()
        else:
            messagebox.showerror("Error", "Ya existe una asignatura con ese nombre.")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecciona una asignatura.")
            return
        item = self.tree.item(selected[0])
        subject_id = item["values"][2]
        subject_name = item["values"][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{subject_name}' y todas sus preguntas?"):
            delete_subject(subject_id)
            self.refresh_list()

    def refresh_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for subject in list_subjects():
            from models.subject import Subject
            q_count = Subject.get_question_count(subject.id)
            self.tree.insert("", "end", values=(subject.name, q_count, subject.id))

    def go_back(self):
        self.frame.destroy()
        self.on_back()

    def show(self):
        self.frame.pack(fill="both", expand=True)