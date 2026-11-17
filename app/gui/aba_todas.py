from tkinter import ttk

from app.agenda import todas_atividades
from app.gui.lista import ListaAtividades


class AbaTodas(ttk.Frame):
    def __init__(self, pai, janela):
        super().__init__(pai, padding=12)
        self.janela = janela
        self.lista = ListaAtividades(self, janela, mostrar_data=True)
        self.lista.pack(fill="both", expand=True)

    def atualizar(self):
        atividades = todas_atividades(self.janela.tarefas, self.janela.eventos)
        self.lista.mostrar([(None, atividades)], vazio="Nenhuma tarefa ou evento cadastrado.")
