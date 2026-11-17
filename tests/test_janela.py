from datetime import date

import pytest

from app.gui.janela import JanelaPrincipal
from app.models import Evento, Tarefa
from app.repositories import EventoRepository, TarefaRepository


@pytest.fixture
def janela(conexao):
    janela = JanelaPrincipal(conexao, hoje=lambda: date(2026, 11, 17))
    janela.withdraw()   # não mostra na tela durante os testes
    yield janela
    janela.destroy()


def test_janela_abre_na_aba_hoje_e_mostra_tarefa(conexao, janela):
    TarefaRepository(conexao).adicionar(Tarefa("Estudar", "2026-11-17"))
    janela.atualizar_tudo()
    assert janela.notebook.tab(janela.notebook.select(), "text") == "Hoje"
    assert janela.aba_hoje.lista.tree.exists("t1")

    janela.alternar_feito("t1")
    assert TarefaRepository(conexao).buscar_por_id(1).feito is True
    assert janela.aba_calendario.lista.tree.exists("t1")
    assert janela.aba_todas.lista.tree.exists("t1")


def test_tarefa_e_evento_com_mesmo_id_nao_se_confundem(conexao, janela):
    TarefaRepository(conexao).adicionar(Tarefa("Estudar", "2026-11-17"))
    EventoRepository(conexao).adicionar(Evento("Reunião", "2026-11-17", "14:30"))
    janela.atualizar_tudo()
    janela.alternar_feito("e1")
    assert EventoRepository(conexao).buscar_por_id(1).feito is True
    assert TarefaRepository(conexao).buscar_por_id(1).feito is False


def test_calendario_destaca_dias_e_troca_de_mes(conexao, janela):
    EventoRepository(conexao).adicionar(Evento("Prova", "2026-11-20", "10:00"))
    janela.atualizar_tudo()
    cal = janela.aba_calendario
    assert date(2026, 11, 20) in cal.dias_destacados
    cal.mes_seguinte()
    assert cal.titulo_mes.cget("text") == "Dezembro 2026"
    cal.voltar_para_hoje()
    assert cal.titulo_mes.cget("text") == "Novembro 2026"
    cal.selecionar(date(2026, 11, 20))
    assert cal.lista.tree.exists("e1")


def test_remover_pede_confirmacao(conexao, janela, monkeypatch):
    TarefaRepository(conexao).adicionar(Tarefa("Estudar", "2026-11-17"))
    janela.atualizar_tudo()
    monkeypatch.setattr("app.gui.janela.messagebox.askyesno", lambda *a, **k: False)
    janela.remover("t1")
    assert TarefaRepository(conexao).buscar_por_id(1) is not None
    monkeypatch.setattr("app.gui.janela.messagebox.askyesno", lambda *a, **k: True)
    janela.remover("t1")
    assert TarefaRepository(conexao).buscar_por_id(1) is None
    assert not janela.aba_hoje.lista.tree.exists("t1")


def test_janela_abre_com_data_malformada_no_banco(conexao):
    conexao.execute("INSERT INTO tarefas (nome, data) VALUES ('velha', '2026-11-1')")
    janela = JanelaPrincipal(conexao, hoje=lambda: date(2026, 11, 17))
    janela.withdraw()
    try:
        assert janela.aba_todas.lista.tree.exists("t1")
    finally:
        janela.destroy()


def test_editar_registro_com_data_malformada_permite_consertar(conexao, janela):
    conexao.execute("INSERT INTO tarefas (nome, data) VALUES ('velha', '20/11/2026')")
    janela.atualizar_tudo()
    formulario = janela.editar("t1")
    assert formulario.data.get() == "20/11/2026"
    formulario.salvar()
    assert TarefaRepository(conexao).buscar_por_id(1).data == "2026-11-20"


def test_aba_hoje_acompanha_a_virada_do_dia(conexao):
    dia = [date(2026, 11, 17)]
    TarefaRepository(conexao).adicionar(Tarefa("Estudar", "2026-11-17"))
    janela = JanelaPrincipal(conexao, hoje=lambda: dia[0])
    janela.withdraw()
    try:
        dia[0] = date(2026, 11, 18)   # passou da meia-noite com o app aberto
        janela.verificar_dia()
        assert janela.aba_hoje.titulo.cget("text") == "Quarta-feira, 18/11/2026"
        assert janela.aba_hoje.lista.tree.item("g0", "values")[-2] == "ATRASADAS"
    finally:
        janela.destroy()
