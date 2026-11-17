import pytest

from app.gui.formulario import montar_evento, montar_tarefa
from app.models import Tarefa


def test_montar_tarefa_conserta_data():
    tarefa = montar_tarefa(" Estudar ", "20-11-26")
    assert (tarefa.nome, tarefa.data) == ("Estudar", "2026-11-20")


def test_montar_tarefa_rejeita_nome_vazio():
    with pytest.raises(ValueError, match="nome não pode ficar vazio"):
        montar_tarefa("  ", "20/11/2026")


def test_montar_tarefa_rejeita_data():
    with pytest.raises(ValueError, match="Data inválida"):
        montar_tarefa("Estudar", "31/02/2026")


def test_montar_tarefa_preserva_id_e_feito():
    original = Tarefa("Estudar", "2026-11-20", feito=True, id=7)
    t = montar_tarefa("Estudar mais", "21/11/2026", original)
    assert (t.id, t.feito, t.nome, t.data) == (7, True, "Estudar mais", "2026-11-21")


def test_montar_evento_conserta_hora_e_rejeita_invalida():
    evento = montar_evento("Reunião", "20/11/2026", "14h", True)
    assert (evento.hora, evento.lembrete) == ("14:00", True)
    with pytest.raises(ValueError, match="Hora inválida"):
        montar_evento("Reunião", "20/11/2026", "25:00", False)
