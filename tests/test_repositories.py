import pytest

from app.models import Evento, Tarefa


def test_adicionar_tarefa_define_id(tarefas):
    t = tarefas.adicionar(Tarefa("Estudar", "2026-11-20"))
    assert t.id is not None


def test_adicionar_tarefa_sem_nome_lanca_erro_e_nao_grava(tarefas):
    with pytest.raises(ValueError):
        tarefas.adicionar(Tarefa("   ", "2026-11-20"))
    assert tarefas.listar() == []


def test_adicionar_tarefa_com_data_invalida_lanca_erro(tarefas):
    with pytest.raises(ValueError):
        tarefas.adicionar(Tarefa("Estudar", "20/11/2026"))
    assert tarefas.listar() == []


def test_atualizar_tarefa_invalida_lanca_erro(tarefas):
    t = tarefas.adicionar(Tarefa("Estudar", "2026-11-20"))
    t.nome = ""
    with pytest.raises(ValueError):
        tarefas.atualizar(t)
    assert tarefas.buscar_por_id(t.id).nome == "Estudar"


def test_listar_retorna_objetos_ordenados_por_data(tarefas):
    tarefas.adicionar(Tarefa("B", "2026-11-22"))
    tarefas.adicionar(Tarefa("A", "2026-11-20"))
    nomes = [t.nome for t in tarefas.listar()]
    assert nomes == ["A", "B"]
    assert isinstance(tarefas.listar()[0], Tarefa)


def test_marcar_como_feito_persiste(tarefas):
    t = tarefas.adicionar(Tarefa("Estudar", "2026-11-20"))
    t.marcar_como_feito()
    assert tarefas.atualizar(t) is True
    assert tarefas.buscar_por_id(t.id).feito is True


def test_remover_tarefa_inexistente_retorna_false(tarefas):
    assert tarefas.remover(999) is False


def test_remover_tarefa(tarefas):
    t = tarefas.adicionar(Tarefa("Estudar", "2026-11-20"))
    assert tarefas.remover(t.id) is True
    assert tarefas.buscar_por_id(t.id) is None


def test_evento_guarda_lembrete_e_feito(eventos):
    # regressão: antes a tabela eventos ficava sem a coluna 'feito' (vírgula faltando)
    e = eventos.adicionar(Evento("Reunião", "2026-11-20", "14:30", lembrete=True))
    lido = eventos.buscar_por_id(e.id)
    assert lido.lembrete is True
    assert lido.feito is False


def test_adicionar_evento_invalido_lanca_erro_e_nao_grava(eventos):
    with pytest.raises(ValueError):
        eventos.adicionar(Evento("Reunião", "2026-11-20", "25:99"))
    assert eventos.listar() == []


def test_atualizar_evento(eventos):
    e = eventos.adicionar(Evento("Reunião", "2026-11-20", "14:30"))
    e.hora = "15:00"
    e.marcar_como_feito()
    assert eventos.atualizar(e) is True
    lido = eventos.buscar_por_id(e.id)
    assert (lido.hora, lido.feito) == ("15:00", True)
