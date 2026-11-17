from main import (
    adicionar_evento,
    adicionar_tarefa,
    alternar_tarefa_feita,
    perguntar_data,
    perguntar_hora,
    perguntar_nome,
)


def respostas(*valores):
    """Simula o que a pessoa digita: cada chamada de entrada() devolve o próximo valor."""
    iterador = iter(valores)
    return lambda _pergunta="": next(iterador)


def test_perguntar_nome_repete_ate_receber_nome(capsys):
    assert perguntar_nome("Nome: ", respostas("", "   ", "Estudar")) == "Estudar"
    assert capsys.readouterr().out.count("não pode ficar vazio") == 2


def test_perguntar_data_no_padrao_brasileiro_nao_mostra_aviso(capsys):
    assert perguntar_data("Data: ", respostas("20/11/2026")) == "2026-11-20"
    assert "entendida" not in capsys.readouterr().out


def test_perguntar_data_conserta_formato_e_avisa_em_dd_mm_aaaa(capsys):
    assert perguntar_data("Data: ", respostas("20-11-26")) == "2026-11-20"
    assert "Data entendida como 20/11/2026" in capsys.readouterr().out


def test_perguntar_data_repete_quando_data_invalida(capsys):
    assert perguntar_data("Data: ", respostas("31/02/2026", "abc", "2026-11-20")) == "2026-11-20"
    assert capsys.readouterr().out.count("Data inválida") == 2


def test_perguntar_hora_repete_quando_hora_invalida(capsys):
    assert perguntar_hora("Hora: ", respostas("25:00", "14h30")) == "14:30"
    assert "Hora inválida" in capsys.readouterr().out


def test_adicionar_tarefa_pelo_menu_grava_no_banco(tarefas):
    adicionar_tarefa(tarefas, respostas("", "Estudar", "data errada", "20/11/2026"))
    [t] = tarefas.listar()
    assert (t.nome, t.data) == ("Estudar", "2026-11-20")


def test_adicionar_evento_pelo_menu_grava_no_banco(eventos):
    adicionar_evento(eventos, respostas("Reunião", "20/11/2026", "14h", "s"))
    [e] = eventos.listar()
    assert (e.nome, e.data, e.hora, e.lembrete) == ("Reunião", "2026-11-20", "14:00", True)


def test_alternar_tarefa_feita(tarefas):
    adicionar_tarefa(tarefas, respostas("Estudar", "2026-11-20"))
    [t] = tarefas.listar()
    alternar_tarefa_feita(tarefas, respostas(str(t.id)))
    assert tarefas.buscar_por_id(t.id).feito is True
    alternar_tarefa_feita(tarefas, respostas(str(t.id)))
    assert tarefas.buscar_por_id(t.id).feito is False
