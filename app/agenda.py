"""O que cada visão da agenda mostra. Sem Tkinter, para poder ser testado."""
import calendar
from datetime import date, timedelta

from app.models import Tarefa, formatar_data_br

# Índice = date.weekday() (segunda = 0). Fixos para não depender do idioma do Windows.
DIAS_SEMANA = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
               "Sexta-feira", "Sábado", "Domingo"]
CABECALHO_SEMANA = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
         "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

DIAS_PROXIMOS = 7
_SEMANAS_NA_GRADE = 6


def ordenar(atividades):
    """Por data, depois hora. Tarefa (sem hora) vem antes dos eventos do mesmo dia."""
    return sorted(atividades, key=lambda a: (a.data, getattr(a, "hora", ""), a.id or 0))


def chave_item(atividade):
    """Identificador único na tela: 't3' para tarefa 3, 'e3' para evento 3."""
    prefixo = "t" if isinstance(atividade, Tarefa) else "e"
    return f"{prefixo}{atividade.id}"


def _no_periodo(tarefas_repo, eventos_repo, inicio, fim):
    return ordenar(tarefas_repo.listar_por_periodo(inicio.isoformat(), fim.isoformat())
                   + eventos_repo.listar_por_periodo(inicio.isoformat(), fim.isoformat()))


def resumo_de_hoje(tarefas_repo, eventos_repo, hoje):
    """Grupos da aba Hoje: atrasadas, hoje e próximos 7 dias."""
    return {
        "atrasadas": ordenar(tarefas_repo.listar_atrasadas(hoje.isoformat())),
        "hoje": _no_periodo(tarefas_repo, eventos_repo, hoje, hoje),
        "proximos": _no_periodo(tarefas_repo, eventos_repo,
                                hoje + timedelta(days=1), hoje + timedelta(days=DIAS_PROXIMOS)),
    }


def atividades_do_dia(tarefas_repo, eventos_repo, dia):
    return _no_periodo(tarefas_repo, eventos_repo, dia, dia)


def todas_atividades(tarefas_repo, eventos_repo):
    return ordenar(tarefas_repo.listar() + eventos_repo.listar())


def dias_com_atividades(tarefas_repo, eventos_repo, ano, mes):
    """Datas do mês que têm pelo menos uma tarefa ou evento."""
    inicio = date(ano, mes, 1)
    fim = date(ano, mes, calendar.monthrange(ano, mes)[1])
    dias = set()
    for atividade in _no_periodo(tarefas_repo, eventos_repo, inicio, fim):
        try:
            dias.add(date.fromisoformat(atividade.data))
        except ValueError:   # dado antigo fora do formato: não destaca, mas não quebra
            continue
    return dias


def semanas_do_mes(ano, mes):
    """Grade do calendário: sempre 6 semanas de 7 dias, começando no domingo."""
    semanas = calendar.Calendar(firstweekday=calendar.SUNDAY).monthdatescalendar(ano, mes)
    while len(semanas) < _SEMANAS_NA_GRADE:
        ultimo = semanas[-1][-1]
        semanas.append([ultimo + timedelta(days=i) for i in range(1, 8)])
    return semanas


def titulo_do_dia(dia):
    """'Terça-feira, 17/11/2026'."""
    return f"{DIAS_SEMANA[dia.weekday()]}, {formatar_data_br(dia.isoformat())}"


def titulo_do_mes(ano, mes):
    """'Novembro 2026'."""
    return f"{MESES[mes - 1]} {ano}"
