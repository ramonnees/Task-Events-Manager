"""Gerenciador de tarefas e eventos.

    python main.py              abre a janela
    python main.py --terminal   abre o menu no terminal
"""
import sys

from app.database import criar_conexao, criar_tabelas
from app.models import (
    Evento,
    Tarefa,
    formatar_data_br,
    normalizar_data,
    normalizar_hora,
)
from app.gui.janela import JanelaPrincipal
from app.repositories import EventoRepository, TarefaRepository

MENU = """
===== Task & Events Manager =====
 1 - Listar tarefas
 2 - Adicionar tarefa
 3 - Marcar/desmarcar tarefa como feita
 4 - Remover tarefa
 5 - Listar eventos
 6 - Adicionar evento
 7 - Marcar/desmarcar evento como feito
 8 - Remover evento
 0 - Sair
"""


# ---------- Leitura do que a pessoa digita ----------
# O parâmetro `entrada` é o input() de verdade no programa; nos testes, é trocado
# por uma função que devolve respostas prontas.

def perguntar_nome(pergunta, entrada=input):
    while True:
        nome = entrada(pergunta).strip()
        if nome:
            return nome
        print("O nome não pode ficar vazio. Digite novamente.")


def perguntar_data(pergunta, entrada=input):
    while True:
        digitado = entrada(pergunta)
        data = normalizar_data(digitado)
        if data:
            data_br = formatar_data_br(data)
            if data_br != digitado.strip():   # só avisa se precisou consertar
                print(f"Data entendida como {data_br}.")
            return data   # volta no formato do banco
        print("Data inválida. Use DD/MM/AAAA (ex.: 20/11/2026). Digite novamente.")


def perguntar_hora(pergunta, entrada=input):
    while True:
        digitado = entrada(pergunta)
        hora = normalizar_hora(digitado)
        if hora:
            if hora != digitado.strip():
                print(f"Hora entendida como {hora}.")
            return hora
        print("Hora inválida. Use HH:MM (ex.: 14:30). Digite novamente.")


def perguntar_sim_nao(pergunta, entrada=input):
    while True:
        resposta = entrada(pergunta).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Responda com s ou n.")


def perguntar_id(pergunta, entrada=input):
    while True:
        digitado = entrada(pergunta).strip()
        if digitado.isdigit():
            return int(digitado)
        print("Digite um número de id válido.")


# ---------- Tarefas ----------

def listar_tarefas(repo):
    lista = repo.listar()
    if not lista:
        print("Nenhuma tarefa cadastrada.")
        return
    for t in lista:
        marca = "[x]" if t.feito else "[ ]"
        aviso = "  (ATRASADA)" if t.atrasada() else ""
        print(f"{t.id:>3} {marca} {t.data_br}  {t.nome}{aviso}")


def adicionar_tarefa(repo, entrada=input):
    nome = perguntar_nome("Nome da tarefa: ", entrada)
    data = perguntar_data("Data (DD/MM/AAAA): ", entrada)
    tarefa = Tarefa(nome, data)
    if not tarefa.eh_valido():   # validação antes de chamar o repositório
        print("Tarefa inválida, nada foi gravado.")
        return
    repo.adicionar(tarefa)
    print(f"Tarefa adicionada (id {tarefa.id}).")


def alternar_tarefa_feita(repo, entrada=input):
    tarefa = repo.buscar_por_id(perguntar_id("Id da tarefa: ", entrada))
    if tarefa is None:
        print("Tarefa não encontrada.")
        return
    if tarefa.feito:
        tarefa.marcar_como_nao_feito()
    else:
        tarefa.marcar_como_feito()
    repo.atualizar(tarefa)
    print("Tarefa marcada como feita." if tarefa.feito else "Tarefa marcada como não feita.")


def remover_tarefa(repo, entrada=input):
    if repo.remover(perguntar_id("Id da tarefa: ", entrada)):
        print("Tarefa removida.")
    else:
        print("Tarefa não encontrada.")


# ---------- Eventos ----------

def _descrever_prazo(dias):
    if dias == 0:
        return "hoje"
    if dias == 1:
        return "amanhã"
    if dias > 1:
        return f"em {dias} dias"
    return "já passou"


def listar_eventos(repo):
    lista = repo.listar()
    if not lista:
        print("Nenhum evento cadastrado.")
        return
    for e in lista:
        marca = "[x]" if e.feito else "[ ]"
        lembrete = "  (lembrete)" if e.lembrete else ""
        prazo = _descrever_prazo(e.dias_restantes())
        print(f"{e.id:>3} {marca} {e.data_br} {e.hora}  {e.nome}"
              f"  - {prazo}{lembrete}")


def adicionar_evento(repo, entrada=input):
    nome = perguntar_nome("Nome do evento: ", entrada)
    data = perguntar_data("Data (DD/MM/AAAA): ", entrada)
    hora = perguntar_hora("Hora (HH:MM): ", entrada)
    lembrete = perguntar_sim_nao("Ativar lembrete? (s/n): ", entrada)
    evento = Evento(nome, data, hora, lembrete=lembrete)
    if not evento.eh_valido():   # validação antes de chamar o repositório
        print("Evento inválido, nada foi gravado.")
        return
    repo.adicionar(evento)
    print(f"Evento adicionado (id {evento.id}).")


def alternar_evento_feito(repo, entrada=input):
    evento = repo.buscar_por_id(perguntar_id("Id do evento: ", entrada))
    if evento is None:
        print("Evento não encontrado.")
        return
    if evento.feito:
        evento.marcar_como_nao_feito()
    else:
        evento.marcar_como_feito()
    repo.atualizar(evento)
    print("Evento marcado como feito." if evento.feito else "Evento marcado como não feito.")


def remover_evento(repo, entrada=input):
    if repo.remover(perguntar_id("Id do evento: ", entrada)):
        print("Evento removido.")
    else:
        print("Evento não encontrado.")


# ---------- Programa principal ----------

def main_terminal():
    conexao = criar_conexao()
    criar_tabelas(conexao)
    tarefas = TarefaRepository(conexao)
    eventos = EventoRepository(conexao)

    acoes = {
        "1": lambda: listar_tarefas(tarefas),
        "2": lambda: adicionar_tarefa(tarefas),
        "3": lambda: alternar_tarefa_feita(tarefas),
        "4": lambda: remover_tarefa(tarefas),
        "5": lambda: listar_eventos(eventos),
        "6": lambda: adicionar_evento(eventos),
        "7": lambda: alternar_evento_feito(eventos),
        "8": lambda: remover_evento(eventos),
    }

    try:
        while True:
            print(MENU)
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "0":
                break
            acao = acoes.get(opcao)
            if acao:
                acao()
            else:
                print("Opção inválida.")
    except (KeyboardInterrupt, EOFError):   # Ctrl+C / Ctrl+Z
        print()
    finally:
        conexao.close()
    print("Até mais!")


def main_janela():
    conexao = criar_conexao()
    criar_tabelas(conexao)
    try:
        JanelaPrincipal(conexao).mainloop()
    finally:
        conexao.close()


def main():
    if "--terminal" in sys.argv:
        main_terminal()
    else:
        main_janela()


if __name__ == "__main__":
    main()
