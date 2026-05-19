import tkinter as tk
from database.db import init_db
from views.menu import MenuView
from views.subjects import SubjectsView
from views.questions import QuestionsView
from views.test import TestView


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Study Tests")
        self.root.geometry("800x650")
        self.root.configure(bg="#2c3e50")
        self.root.minsize(700, 600)

        init_db()
        self.show_menu()

    def clear_content(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_menu(self):
        self.clear_content()
        self.root.configure(bg="#2c3e50")
        MenuView(
            self.root,
            on_subjects=self.show_subjects,
            on_add_questions=self.show_questions,
            on_do_test=self.show_test
        )

    def show_subjects(self):
        self.clear_content()
        SubjectsView(self.root, on_back=self.show_menu).show()

    def show_questions(self):
        self.clear_content()
        QuestionsView(self.root, on_back=self.show_menu).show()

    def show_test(self):
        self.clear_content()
        TestView(self.root, on_back=self.show_menu).show()


if __name__ == "__main__":
    app = App()
    app.root.mainloop()