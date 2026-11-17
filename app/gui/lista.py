"""Lista de tarefas e eventos usada nas três abas."""
import tkinter as tk
from tkinter import font, ttk

from app.agenda import chave_item
from app.models import Tarefa, formatar_data_br

COLUNAS = ("feito", "tipo", "data", "hora", "nome", "info")
TITULOS = {"feito": "", "tipo": "Tipo", "data": "Data", "hora": "Hora", "nome": "Nome", "info": ""}
LARGURAS = {"feito": 40, "tipo": 70, "data": 90, "hora": 60, "nome": 320, "info": 110}

COR_FEITO = "#9ca3af"
COR_ATRASADA = "#b91c1c"


def _eh_atividade(iid):
    """Linhas de cabeçalho ('g0') e de aviso ('vazio') não são tarefas nem eventos."""
    return bool(iid) and iid[0] in "te" and iid[1:].isdigit()


class ListaAtividades(ttk.Frame):
    def __init__(self, pai, janela, mostrar_data):
        super().__init__(pai)
        self.janela = janela
        self.colunas = COLUNAS if mostrar_data else tuple(c for c in COLUNAS if c != "data")

        self.tree = ttk.Treeview(self, columns=self.colunas, show="headings", selectmode="browse")
        for coluna in self.colunas:
            self.tree.heading(coluna, text=TITULOS[coluna])
            self.tree.column(coluna, width=LARGURAS[coluna], stretch=(coluna == "nome"),
                             anchor="w" if coluna in ("nome", "info", "tipo") else "center")

        negrito = font.nametofont("TkDefaultFont").copy()
        negrito.configure(weight="bold")
        self.tree.tag_configure("grupo", font=negrito)
        self.tree.tag_configure("feito", foreground=COR_FEITO)
        self.tree.tag_configure("atrasada", foreground=COR_ATRASADA)

        rolagem = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=rolagem.set)
        self.tree.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")

        self.tree.bind("<Button-1>", self._clique)
        self.tree.bind("<Double-1>", self._duplo_clique)
        self.tree.bind("<space>", lambda _e: self._na_selecao(janela.alternar_feito))
        self.tree.bind("<Delete>", lambda _e: self._na_selecao(janela.remover))

    def selecionado(self):
        """Chave ('t3'/'e3') da linha selecionada, ou None."""
        selecao = self.tree.selection()
        return selecao[0] if selecao and _eh_atividade(selecao[0]) else None

    def mostrar(self, grupos, vazio=None):
        """grupos: lista de (titulo ou None, atividades)."""
        anterior = self.selecionado()
        self.tree.delete(*self.tree.get_children())

        if not any(itens for _titulo, itens in grupos):
            if vazio:
                self.tree.insert("", "end", iid="vazio", values=self._linha(nome=vazio),
                                 tags=("grupo",))
            return

        for n, (titulo, itens) in enumerate(grupos):
            if titulo:
                self.tree.insert("", "end", iid=f"g{n}", values=self._linha(nome=titulo),
                                 tags=("grupo",))
            for atividade in itens:
                self.tree.insert("", "end", iid=chave_item(atividade),
                                 values=self._valores(atividade), tags=self._tags(atividade))

        if anterior and self.tree.exists(anterior):
            self.tree.selection_set(anterior)
            self.tree.focus(anterior)
            self.tree.see(anterior)

    def _linha(self, **campos):
        return [campos.get(coluna, "") for coluna in self.colunas]

    def _valores(self, atividade):
        eh_tarefa = isinstance(atividade, Tarefa)
        try:
            data = formatar_data_br(atividade.data)
        except ValueError:   # dado antigo fora do formato: mostra como está
            data = atividade.data
        if eh_tarefa:
            info = "(ATRASADA)" if self._atrasada(atividade) else ""
        else:
            info = "(lembrete)" if atividade.lembrete else ""
        return self._linha(
            feito="[x]" if atividade.feito else "[ ]",
            tipo="Tarefa" if eh_tarefa else "Evento",
            data=data,
            hora="" if eh_tarefa else atividade.hora,
            nome=atividade.nome,
            info=info,
        )

    def _atrasada(self, tarefa):
        try:
            return tarefa.atrasada(self.janela.hoje())
        except ValueError:
            return False

    def _tags(self, atividade):
        if atividade.feito:
            return ("feito",)
        if isinstance(atividade, Tarefa) and self._atrasada(atividade):
            return ("atrasada",)
        return ()

    def _na_selecao(self, acao):
        chave = self.selecionado()
        if chave:
            acao(chave)
        return "break"

    def _clique(self, evento):
        # clique na coluna [ ] marca/desmarca
        if self.tree.identify_region(evento.x, evento.y) != "cell":
            return None
        if self.tree.identify_column(evento.x) != "#1":
            return None
        chave = self.tree.identify_row(evento.y)
        if _eh_atividade(chave):
            self.tree.selection_set(chave)
            self.janela.alternar_feito(chave)
            return "break"
        return None

    def _duplo_clique(self, evento):
        chave = self.tree.identify_row(evento.y)
        if _eh_atividade(chave):
            self.janela.editar(chave)
        return "break"
