from tkinter import ttk

from app.agenda import resumo_de_hoje, titulo_do_dia
from app.gui.lista import ListaAtividades

GRUPOS = [("ATRASADAS", "atrasadas"), ("HOJE", "hoje"), ("PRÓXIMOS 7 DIAS", "proximos")]
MENSAGEM_VAZIA = "Nada para hoje. Use + Tarefa ou + Evento."


class AbaHoje(ttk.Frame):
    def __init__(self, pai, janela):
        super().__init__(pai, padding=12)
        self.janela = janela

        topo = ttk.Frame(self)
        topo.pack(fill="x", pady=(0, 8))
        self.titulo = ttk.Label(topo, style="Titulo.TLabel")
        self.titulo.pack(side="left")
        ttk.Button(topo, text="+ Evento",
                   command=lambda: janela.nova("evento", janela.hoje())).pack(side="right")
        ttk.Button(topo, text="+ Tarefa",
                   command=lambda: janela.nova("tarefa", janela.hoje())).pack(side="right", padx=(0, 8))

        self.lista = ListaAtividades(self, janela, mostrar_data=True)
        self.lista.pack(fill="both", expand=True)

    def atualizar(self):
        hoje = self.janela.hoje()
        self.titulo.config(text=titulo_do_dia(hoje))
        resumo = resumo_de_hoje(self.janela.tarefas, self.janela.eventos, hoje)
        grupos = [(titulo, resumo[chave]) for titulo, chave in GRUPOS if resumo[chave]]
        self.lista.mostrar(grupos, vazio=MENSAGEM_VAZIA)
