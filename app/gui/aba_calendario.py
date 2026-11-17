import tkinter as tk
from tkinter import font, ttk

from app.agenda import (
    CABECALHO_SEMANA,
    atividades_do_dia,
    dias_com_atividades,
    semanas_do_mes,
    titulo_do_dia,
    titulo_do_mes,
)
from app.gui.lista import ListaAtividades

COR_COM_ATIVIDADE = "#dbeafe"
COR_SELECIONADO = "#93c5fd"
COR_OUTRO_MES = "#9ca3af"
COR_TEXTO = "#111827"


class AbaCalendario(ttk.Frame):
    def __init__(self, pai, janela):
        super().__init__(pai, padding=12)
        self.janela = janela
        hoje = janela.hoje()
        self.ano, self.mes = hoje.year, hoje.month
        self.selecionado = hoje
        self.dias_destacados = set()

        self.fonte_normal = font.nametofont("TkDefaultFont").copy()
        self.fonte_negrito = self.fonte_normal.copy()
        self.fonte_negrito.configure(weight="bold")

        nav = ttk.Frame(self)
        nav.pack(pady=(0, 8))
        ttk.Button(nav, text="◀", width=3, command=self.mes_anterior).pack(side="left")
        self.titulo_mes = ttk.Label(nav, style="Titulo.TLabel", width=16, anchor="center")
        self.titulo_mes.pack(side="left", padx=8)
        ttk.Button(nav, text="▶", width=3, command=self.mes_seguinte).pack(side="left")
        ttk.Button(nav, text="Hoje", command=self.voltar_para_hoje).pack(side="left", padx=(16, 0))

        grade = ttk.Frame(self)
        grade.pack()
        for coluna, nome in enumerate(CABECALHO_SEMANA):
            ttk.Label(grade, text=nome, anchor="center", width=6).grid(row=0, column=coluna)
        self.botoes = []
        for linha in range(6):
            botoes_da_semana = []
            for coluna in range(7):
                botao = tk.Button(grade, width=5, relief="flat", bd=1, cursor="hand2")
                botao.grid(row=linha + 1, column=coluna, padx=1, pady=1)
                botoes_da_semana.append(botao)
            self.botoes.append(botoes_da_semana)
        self.fundo_padrao = self.botoes[0][0].cget("bg")

        dia = ttk.Frame(self)
        dia.pack(fill="x", pady=(12, 8))
        self.titulo_dia = ttk.Label(dia, style="Subtitulo.TLabel")
        self.titulo_dia.pack(side="left")
        ttk.Button(dia, text="+ Evento",
                   command=lambda: janela.nova("evento", self.selecionado)).pack(side="right")
        ttk.Button(dia, text="+ Tarefa",
                   command=lambda: janela.nova("tarefa", self.selecionado)).pack(side="right", padx=(0, 8))

        self.lista = ListaAtividades(self, janela, mostrar_data=False)
        self.lista.pack(fill="both", expand=True)

    def atualizar(self):
        janela = self.janela
        hoje = janela.hoje()
        self.titulo_mes.config(text=titulo_do_mes(self.ano, self.mes))
        self.dias_destacados = dias_com_atividades(janela.tarefas, janela.eventos, self.ano, self.mes)

        for linha, semana in enumerate(semanas_do_mes(self.ano, self.mes)):
            for coluna, dia in enumerate(semana):
                destacado = dia in self.dias_destacados
                if dia == self.selecionado:
                    fundo = COR_SELECIONADO
                elif destacado:
                    fundo = COR_COM_ATIVIDADE
                else:
                    fundo = self.fundo_padrao
                self.botoes[linha][coluna].config(
                    text=str(dia.day),
                    bg=fundo,
                    activebackground=COR_SELECIONADO,
                    fg=COR_TEXTO if dia.month == self.mes else COR_OUTRO_MES,
                    font=self.fonte_negrito if destacado else self.fonte_normal,
                    relief="solid" if dia == hoje else "flat",
                    command=lambda d=dia: self.selecionar(d),
                )

        self.titulo_dia.config(text=titulo_do_dia(self.selecionado))
        atividades = atividades_do_dia(janela.tarefas, janela.eventos, self.selecionado)
        self.lista.mostrar([(None, atividades)], vazio="Nada neste dia.")

    def selecionar(self, dia):
        self.selecionado = dia
        self.ano, self.mes = dia.year, dia.month   # clicar num dia de outro mês troca o mês
        self.atualizar()

    def mes_anterior(self):
        self.ano, self.mes = (self.ano - 1, 12) if self.mes == 1 else (self.ano, self.mes - 1)
        self.atualizar()

    def mes_seguinte(self):
        self.ano, self.mes = (self.ano + 1, 1) if self.mes == 12 else (self.ano, self.mes + 1)
        self.atualizar()

    def voltar_para_hoje(self):
        self.selecionar(self.janela.hoje())
