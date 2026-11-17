"""Formulário (janela pequena) para criar ou editar tarefas e eventos."""
import tkinter as tk
from tkinter import ttk

from app.models import Evento, Tarefa, formatar_data_br, normalizar_data, normalizar_hora

ERRO_NOME = "O nome não pode ficar vazio."
ERRO_DATA = "Data inválida. Use DD/MM/AAAA (ex.: 20/11/2026)."
ERRO_HORA = "Hora inválida. Use HH:MM (ex.: 14:30)."

COR_ERRO = "#b91c1c"


def _validar_nome_e_data(nome, data_txt):
    nome = (nome or "").strip()
    if not nome:
        raise ValueError(ERRO_NOME)
    data = normalizar_data(data_txt)
    if data is None:
        raise ValueError(ERRO_DATA)
    return nome, data


def montar_tarefa(nome, data_txt, original=None):
    """Cria a Tarefa a partir do que foi digitado. Lança ValueError com a mensagem da tela."""
    nome, data = _validar_nome_e_data(nome, data_txt)
    if original is None:
        return Tarefa(nome, data)
    return Tarefa(nome, data, feito=original.feito, id=original.id)


def montar_evento(nome, data_txt, hora_txt, lembrete, original=None):
    """Cria o Evento a partir do que foi digitado. Lança ValueError com a mensagem da tela."""
    nome, data = _validar_nome_e_data(nome, data_txt)
    hora = normalizar_hora(hora_txt)
    if hora is None:
        raise ValueError(ERRO_HORA)
    if original is None:
        return Evento(nome, data, hora, lembrete=lembrete)
    return Evento(nome, data, hora, lembrete=lembrete, feito=original.feito, id=original.id)


class FormularioAtividade(tk.Toplevel):
    """Janela modal. Se o que foi digitado estiver errado, mostra o erro e não fecha."""

    def __init__(self, pai, tipo, data_inicial, original=None, ao_salvar=None):
        super().__init__(pai)
        self.tipo = tipo
        self.original = original
        self.ao_salvar = ao_salvar

        acao = "Editar" if original else "Nova" if tipo == "tarefa" else "Novo"
        self.title(f"{acao} {tipo}")
        self.resizable(False, False)
        self.transient(pai)

        corpo = ttk.Frame(self, padding=16)
        corpo.grid(sticky="nsew")

        self.nome = tk.StringVar(value=original.nome if original else "")
        data_iso = original.data if original else data_inicial.isoformat()
        self.data = tk.StringVar(value=formatar_data_br(data_iso))

        linha = self._campo(corpo, 0, "Nome:", self.nome, largura=32)
        self._campo(corpo, 1, "Data (DD/MM/AAAA):", self.data, largura=12)

        if tipo == "evento":
            self.hora = tk.StringVar(value=original.hora if original else "")
            self.lembrete = tk.BooleanVar(value=original.lembrete if original else False)
            self._campo(corpo, 2, "Hora (HH:MM):", self.hora, largura=8)
            ttk.Checkbutton(corpo, text="Lembrete", variable=self.lembrete).grid(
                row=3, column=1, sticky="w", pady=4)

        self.erro = ttk.Label(corpo, foreground=COR_ERRO, wraplength=320)
        self.erro.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))

        botoes = ttk.Frame(corpo)
        botoes.grid(row=5, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(botoes, text="Cancelar", command=self.destroy).pack(side="right")
        ttk.Button(botoes, text="Salvar", command=self.salvar).pack(side="right", padx=(0, 8))

        self.bind("<Return>", lambda _e: self.salvar())
        self.bind("<Escape>", lambda _e: self.destroy())
        linha.focus_set()
        self.grab_set()

    @staticmethod
    def _campo(pai, linha, rotulo, variavel, largura):
        ttk.Label(pai, text=rotulo).grid(row=linha, column=0, sticky="w", pady=4, padx=(0, 8))
        entrada = ttk.Entry(pai, textvariable=variavel, width=largura)
        entrada.grid(row=linha, column=1, sticky="w", pady=4)
        return entrada

    def montar(self):
        if self.tipo == "tarefa":
            return montar_tarefa(self.nome.get(), self.data.get(), self.original)
        return montar_evento(self.nome.get(), self.data.get(), self.hora.get(),
                             self.lembrete.get(), self.original)

    def salvar(self):
        try:
            atividade = self.montar()
        except ValueError as erro:
            self.erro.config(text=str(erro))
            return
        # mostra como o programa entendeu (ex.: 20-11-26 vira 20/11/2026)
        self.data.set(atividade.data_br)
        if self.tipo == "evento":
            self.hora.set(atividade.hora)
        if self.ao_salvar:
            self.ao_salvar(atividade)
        self.destroy()
