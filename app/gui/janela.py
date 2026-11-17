"""Janela principal: abas Hoje, Calendário e Todas."""
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from app.gui.aba_calendario import AbaCalendario
from app.gui.aba_hoje import AbaHoje
from app.gui.aba_todas import AbaTodas
from app.gui.formulario import FormularioAtividade
from app.models import Tarefa
from app.repositories import EventoRepository, TarefaRepository

DICA = "Espaço: marcar/desmarcar  ·  Duplo clique: editar  ·  Delete: remover"
VERIFICAR_DIA_MS = 60_000   # confere a cada minuto se o dia virou


class JanelaPrincipal(tk.Tk):
    def __init__(self, conexao, hoje=date.today):
        super().__init__()
        self.hoje = hoje
        self.tarefas = TarefaRepository(conexao)
        self.eventos = EventoRepository(conexao)

        self.title("Task & Events Manager")
        self.geometry("800x600")
        self.minsize(640, 520)

        estilo = ttk.Style(self)
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 14, "bold"))
        estilo.configure("Subtitulo.TLabel", font=("Segoe UI", 11, "bold"))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(8, 0))
        self.aba_hoje = AbaHoje(self.notebook, self)
        self.aba_calendario = AbaCalendario(self.notebook, self)
        self.aba_todas = AbaTodas(self.notebook, self)
        self.notebook.add(self.aba_hoje, text="Hoje")
        self.notebook.add(self.aba_calendario, text="Calendário")
        self.notebook.add(self.aba_todas, text="Todas")
        self.notebook.select(self.aba_hoje)

        rodape = ttk.Frame(self, padding=8)
        rodape.pack(fill="x")
        ttk.Label(rodape, text=DICA, foreground="#6b7280").pack(side="left")
        ttk.Button(rodape, text="Remover",
                   command=lambda: self._na_selecao(self.remover)).pack(side="right")
        ttk.Button(rodape, text="Editar",
                   command=lambda: self._na_selecao(self.editar)).pack(side="right", padx=4)
        ttk.Button(rodape, text="Marcar/desmarcar",
                   command=lambda: self._na_selecao(self.alternar_feito)).pack(side="right")

        self.atualizar_tudo()

        # Se o app ficar aberto de um dia para o outro, a aba Hoje precisa acompanhar.
        self.notebook.bind("<<NotebookTabChanged>>", lambda _e: self.verificar_dia())
        self.bind("<FocusIn>", lambda _e: self.verificar_dia())
        self._timer = self.after(VERIFICAR_DIA_MS, self._verificar_dia_periodicamente)

    # ---------- atualização ----------

    def atualizar_tudo(self):
        self._dia_mostrado = self.hoje()
        for aba in (self.aba_hoje, self.aba_calendario, self.aba_todas):
            aba.atualizar()

    def verificar_dia(self):
        """Atualiza tudo se o dia mudou desde a última atualização (passou da meia-noite)."""
        if self.hoje() != self._dia_mostrado:
            self.atualizar_tudo()

    def _verificar_dia_periodicamente(self):
        self.verificar_dia()
        self._timer = self.after(VERIFICAR_DIA_MS, self._verificar_dia_periodicamente)

    def destroy(self):
        self.after_cancel(self._timer)
        super().destroy()

    # ---------- ações ----------

    def _repo(self, atividade):
        return self.tarefas if isinstance(atividade, Tarefa) else self.eventos

    def buscar(self, chave):
        """'t3' -> Tarefa 3, 'e3' -> Evento 3 (ou None)."""
        repo = self.tarefas if chave[0] == "t" else self.eventos
        return repo.buscar_por_id(int(chave[1:]))

    def _salvar(self, atividade):
        repo = self._repo(atividade)
        try:
            if atividade.id is None:
                repo.adicionar(atividade)
            else:
                repo.atualizar(atividade)
        except ValueError as erro:
            messagebox.showerror("Não foi possível salvar", str(erro), parent=self)
            return
        self.atualizar_tudo()

    def nova(self, tipo, dia):
        return FormularioAtividade(self, tipo, dia, ao_salvar=self._salvar)

    def editar(self, chave):
        atividade = self.buscar(chave)
        if atividade is None:
            return None
        tipo = "tarefa" if isinstance(atividade, Tarefa) else "evento"
        return FormularioAtividade(self, tipo, self.hoje(), original=atividade,
                                   ao_salvar=self._salvar)

    def alternar_feito(self, chave):
        atividade = self.buscar(chave)
        if atividade is None:
            return
        if atividade.feito:
            atividade.marcar_como_nao_feito()
        else:
            atividade.marcar_como_feito()
        self._salvar(atividade)

    def remover(self, chave):
        atividade = self.buscar(chave)
        if atividade is None:
            return
        if messagebox.askyesno("Remover", f"Remover '{atividade.nome}'?", parent=self):
            self._repo(atividade).remover(atividade.id)
            self.atualizar_tudo()

    def _na_selecao(self, acao):
        aba = self.nametowidget(self.notebook.select())
        chave = aba.lista.selecionado()
        if chave:
            acao(chave)
