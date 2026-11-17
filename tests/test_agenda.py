from datetime import date

from app.agenda import (
    atividades_do_dia,
    chave_item,
    dias_com_atividades,
    ordenar,
    resumo_de_hoje,
    semanas_do_mes,
    titulo_do_dia,
    titulo_do_mes,
    todas_atividades,
)
from app.models import Evento, Tarefa

HOJE = date(2026, 11, 17)   # terça-feira


def test_resumo_de_hoje_separa_grupos(tarefas, eventos):
    tarefas.adicionar(Tarefa("atrasada", "2026-11-15"))
    tarefas.adicionar(Tarefa("hoje", "2026-11-17"))
    eventos.adicionar(Evento("reuniao", "2026-11-17", "14:30"))
    eventos.adicionar(Evento("prova", "2026-11-24", "10:00"))     # hoje+7: entra
    eventos.adicionar(Evento("longe", "2026-11-25", "10:00"))     # hoje+8: fora
    eventos.adicionar(Evento("passado", "2026-11-10", "10:00"))   # evento passado: fora
    r = resumo_de_hoje(tarefas, eventos, HOJE)
    assert [a.nome for a in r["atrasadas"]] == ["atrasada"]
    assert [a.nome for a in r["hoje"]] == ["hoje", "reuniao"]
    assert [a.nome for a in r["proximos"]] == ["prova"]


def test_resumo_de_hoje_atravessa_ano(tarefas, eventos):
    eventos.adicionar(Evento("ano novo", "2027-01-01", "00:00"))
    r = resumo_de_hoje(tarefas, eventos, date(2026, 12, 28))
    assert [a.nome for a in r["proximos"]] == ["ano novo"]


def test_ordenar_aceita_tarefa_sem_hora():
    lista = [Evento("e", "2026-11-17", "08:00", id=1), Tarefa("t", "2026-11-17", id=1)]
    assert [a.nome for a in ordenar(lista)] == ["t", "e"]


def test_chave_item_distingue_tipo():
    assert chave_item(Tarefa("a", "2026-11-17", id=3)) == "t3"
    assert chave_item(Evento("a", "2026-11-17", "10:00", id=3)) == "e3"


def test_dias_com_atividades(tarefas, eventos):
    tarefas.adicionar(Tarefa("a", "2026-11-17"))
    eventos.adicionar(Evento("b", "2026-11-20", "10:00"))
    eventos.adicionar(Evento("c", "2026-12-01", "10:00"))
    assert dias_com_atividades(tarefas, eventos, 2026, 11) == {date(2026, 11, 17), date(2026, 11, 20)}


def test_semanas_do_mes_comeca_no_domingo():
    semanas = semanas_do_mes(2026, 11)
    assert semanas[0][0] == date(2026, 11, 1)        # 01/11/2026 é domingo
    assert all(s[0].weekday() == 6 for s in semanas)


def test_semanas_do_mes_sempre_6_semanas():
    for ano, mes in [(2026, 2), (2026, 11), (2027, 1)]:
        semanas = semanas_do_mes(ano, mes)
        assert len(semanas) == 6 and all(len(s) == 7 for s in semanas)


def test_titulos():
    assert titulo_do_dia(HOJE) == "Terça-feira, 17/11/2026"
    assert titulo_do_mes(2026, 3) == "Março 2026"


def test_atividades_do_dia_e_todas(tarefas, eventos):
    eventos.adicionar(Evento("reuniao", "2026-11-17", "14:30"))
    tarefas.adicionar(Tarefa("estudar", "2026-11-17"))
    tarefas.adicionar(Tarefa("outra", "2026-11-18"))
    assert [a.nome for a in atividades_do_dia(tarefas, eventos, HOJE)] == ["estudar", "reuniao"]
    assert [a.nome for a in todas_atividades(tarefas, eventos)] == ["estudar", "reuniao", "outra"]


def test_dias_com_atividades_ignora_data_malformada_no_banco(tarefas, eventos):
    # dado antigo, gravado antes da validação existir
    tarefas.conexao.execute("INSERT INTO tarefas (nome, data) VALUES ('velha', '2026-11-1')")
    tarefas.adicionar(Tarefa("ok", "2026-11-17"))
    assert dias_com_atividades(tarefas, eventos, 2026, 11) == {date(2026, 11, 17)}
