from datetime import date

import pytest

from app.models import Evento, Tarefa, formatar_data_br, normalizar_data, normalizar_hora


def test_formatar_data_br():
    assert formatar_data_br("2026-11-20") == "20/11/2026"
    assert formatar_data_br("2026-03-05") == "05/03/2026"


def test_tarefa_e_evento_mostram_data_no_padrao_brasileiro():
    tarefa = Tarefa("Estudar", "2026-11-20")
    evento = Evento("Reunião", "2026-11-20", "14:30")
    assert tarefa.data_br == "20/11/2026"
    assert evento.data_br == "20/11/2026"
    assert "20/11/2026" in repr(tarefa)
    assert "20/11/2026" in repr(evento)


def test_tarefa_valida():
    assert Tarefa("Estudar SQL", "2026-11-20").eh_valido()


def test_tarefa_rejeita_nome_vazio_ou_nulo():
    assert not Tarefa("   ", "2026-11-20").eh_valido()
    assert not Tarefa(None, "2026-11-20").eh_valido()


def test_tarefa_rejeita_data_invalida():
    assert not Tarefa("Estudar", "20/11/2026").eh_valido()
    assert not Tarefa("Estudar", "").eh_valido()


def test_tarefa_atrasada():
    hoje = date(2026, 11, 20)
    assert Tarefa("a", "2026-11-19").atrasada(hoje)
    assert not Tarefa("a", "2026-11-20").atrasada(hoje)      # vence hoje: ainda não atrasou
    assert not Tarefa("a", "2026-11-19", feito=True).atrasada(hoje)


def test_evento_valido_e_hora_invalida():
    assert Evento("Reunião", "2026-11-20", "14:30").eh_valido()
    assert not Evento("Reunião", "2026-11-20", "25:99").eh_valido()


def test_evento_dias_restantes():
    hoje = date(2026, 11, 20)
    assert Evento("a", "2026-11-25", "10:00").dias_restantes(hoje) == 5
    assert Evento("a", "2026-11-18", "10:00").dias_restantes(hoje) == -2


@pytest.mark.parametrize("digitado", [
    "2026-11-20",
    "20/11/2026",
    "20-11-2026",
    "20.11.2026",
    "2026/11/20",
    "20/11/26",
    "20112026",
    "  20/11/2026  ",
])
def test_normalizar_data_conserta_formatos_comuns(digitado):
    assert normalizar_data(digitado) == "2026-11-20"


def test_normalizar_data_aceita_dia_e_mes_com_um_digito():
    assert normalizar_data("5/3/2026") == "2026-03-05"


@pytest.mark.parametrize("digitado", ["31/02/2026", "abc", "", "   ", None, "32/01/2026"])
def test_normalizar_data_retorna_none_quando_nao_tem_conserto(digitado):
    assert normalizar_data(digitado) is None


@pytest.mark.parametrize("digitado, esperado", [
    ("14:30", "14:30"),
    ("14h30", "14:30"),
    ("14H30", "14:30"),
    ("14h", "14:00"),
    ("1430", "14:30"),
    ("9:05", "09:05"),
    ("930", "09:30"),
])
def test_normalizar_hora_conserta_formatos_comuns(digitado, esperado):
    assert normalizar_hora(digitado) == esperado


@pytest.mark.parametrize("digitado", ["25:00", "14:60", "abc", "", None])
def test_normalizar_hora_retorna_none_quando_nao_tem_conserto(digitado):
    assert normalizar_hora(digitado) is None
