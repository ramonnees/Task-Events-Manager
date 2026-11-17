# Interface gráfica (Tkinter) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Janela Tkinter com abas Hoje / Calendário / Todas para adicionar, editar, marcar e remover tarefas e eventos.

**Architecture:** A lógica das visões fica em `app/agenda.py` (sem Tkinter, testada com pytest). O código da janela fica em `app/gui/` e só chama `agenda`, `models` e `repositories`. `main.py` abre a janela; com `--terminal` abre o menu antigo.

**Tech Stack:** Python 3.13, tkinter/ttk 8.6, sqlite3, pytest.

**Spec:** `docs/superpowers/specs/2026-11-17-interface-grafica-design.md`

## Global Constraints

- Nenhum SQL ou regra de negócio em `app/gui/`.
- Banco guarda AAAA-MM-DD. Tela mostra DD/MM/AAAA (`formatar_data_br`).
- Formulário inválido: mensagem em vermelho, formulário **não fecha**.
- Semana do calendário começa no **domingo**. Grade sempre com 6 semanas × 7 dias.
- "Próximos dias" = de amanhã até hoje+7 (inclusive).
- Eventos passados não são "atrasados". Só tarefas não feitas com data < hoje.
- Nomes de dias e meses em português fixos no código (não usar `locale`).
- Nada a instalar além do Python.
- Imports no topo dos arquivos. Testes usam as fixtures de `tests/conftest.py`.
- Commits locais ao fim de cada tarefa. `git push` só com o OK do Ramon.

## Review Focus

1. Data inválida já gravada no banco (dados antigos): a listagem não pode quebrar. A janela deve abrir mesmo assim. → teste na Task 2 (`test_ordenar_aceita_tarefa_sem_hora`) cobre a ordenação; a lista exibe a data crua se `formatar_data_br` falhar (Task 4).
2. Mês com 4 ou 5 semanas (ex.: fevereiro de 2026 começa no domingo) precisa virar 6 linhas. → `test_semanas_do_mes_sempre_6_semanas` (Task 2).
3. Virada de ano nos "próximos 7 dias" (28/12 → 04/01). → `test_resumo_de_hoje_atravessa_ano` (Task 2).
4. Editar uma tarefa sem mudar nada não pode duplicar o registro. → `test_montar_tarefa_preserva_id_e_feito` (Task 3).
5. Tarefa e evento com o mesmo id: ações na lista atingem o item certo. → `test_chave_item_distingue_tipo` (Task 2).

---

### Task 1: Consultas por período no repositório

**Files:**
- Modify: `app/repositories.py`
- Test: `tests/test_repositories.py`

**Interfaces:**
- Produces:
  - `TarefaRepository.listar_por_periodo(inicio: str, fim: str) -> list[Tarefa]` (ISO, inclusive, `ORDER BY data, id`)
  - `TarefaRepository.listar_atrasadas(hoje: str) -> list[Tarefa]` (`feito = 0 AND data < hoje`, `ORDER BY data, id`)
  - `EventoRepository.listar_por_periodo(inicio: str, fim: str) -> list[Evento]` (`ORDER BY data, hora, id`)

- [ ] **Step 1: Testes que falham**

```python
def test_tarefas_listar_por_periodo_inclui_limites(tarefas):
    for d in ["2026-11-16", "2026-11-17", "2026-11-20", "2026-11-21"]:
        tarefas.adicionar(Tarefa(d, d))
    assert [t.data for t in tarefas.listar_por_periodo("2026-11-17", "2026-11-20")] == ["2026-11-17", "2026-11-20"]

def test_listar_atrasadas_ignora_feitas_e_hoje(tarefas):
    tarefas.adicionar(Tarefa("velha", "2026-11-15"))
    tarefas.adicionar(Tarefa("feita", "2026-11-15", feito=True))
    tarefas.adicionar(Tarefa("hoje", "2026-11-17"))
    assert [t.nome for t in tarefas.listar_atrasadas("2026-11-17")] == ["velha"]

def test_eventos_listar_por_periodo_ordena_por_hora(eventos):
    eventos.adicionar(Evento("tarde", "2026-11-17", "15:00"))
    eventos.adicionar(Evento("manha", "2026-11-17", "09:00"))
    eventos.adicionar(Evento("fora", "2026-11-25", "09:00"))
    assert [e.nome for e in eventos.listar_por_periodo("2026-11-17", "2026-11-20")] == ["manha", "tarde"]
```

- [ ] **Step 2:** `python -m pytest tests/test_repositories.py -q`. Esperado: 3 FAIL (`AttributeError`).
- [ ] **Step 3:** Implementar os três métodos com `WHERE data BETWEEN ? AND ?` / `data < ?`, reaproveitando `_para_objeto`.
- [ ] **Step 4:** `python -m pytest -q`. Esperado: tudo PASS.
- [ ] **Step 5:** `git commit -m "Adiciona consultas por periodo e tarefas atrasadas"`

---

### Task 2: Lógica das visões (`app/agenda.py`)

**Files:**
- Create: `app/agenda.py`
- Test: `tests/test_agenda.py`

**Interfaces:**
- Consumes: Task 1, `formatar_data_br`, `FORMATO_DATA` de `app.models`.
- Produces:
  - `DIAS_SEMANA: list[str]` = `["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]` (índice = `date.weekday()`)
  - `CABECALHO_SEMANA: list[str]` = `["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]`
  - `MESES: list[str]` = `["Janeiro", ..., "Dezembro"]`
  - `ordenar(atividades: list) -> list` (chave: `(data, getattr(a, "hora", ""), id)`. Tarefa sem hora vem antes dos eventos do mesmo dia.)
  - `chave_item(atividade) -> str` → `"t<id>"` ou `"e<id>"`
  - `resumo_de_hoje(tarefas_repo, eventos_repo, hoje: date) -> dict[str, list]` com chaves `"atrasadas"`, `"hoje"`, `"proximos"`, cada uma já ordenada
  - `atividades_do_dia(tarefas_repo, eventos_repo, dia: date) -> list`
  - `todas_atividades(tarefas_repo, eventos_repo) -> list`
  - `dias_com_atividades(tarefas_repo, eventos_repo, ano: int, mes: int) -> set[date]`
  - `semanas_do_mes(ano: int, mes: int) -> list[list[date]]` (6 × 7, domingo primeiro)
  - `titulo_do_dia(dia: date) -> str` → `"Terça-feira, 17/11/2026"`
  - `titulo_do_mes(ano: int, mes: int) -> str` → `"Novembro 2026"`

- [ ] **Step 1: Testes que falham** (`HOJE = date(2026, 11, 17)`, terça-feira)

```python
def test_resumo_de_hoje_separa_grupos(tarefas, eventos):
    tarefas.adicionar(Tarefa("atrasada", "2026-11-15"))
    tarefas.adicionar(Tarefa("hoje", "2026-11-17"))
    eventos.adicionar(Evento("reuniao", "2026-11-17", "14:30"))
    eventos.adicionar(Evento("prova", "2026-11-24", "10:00"))   # hoje+7: entra
    eventos.adicionar(Evento("longe", "2026-11-25", "10:00"))   # hoje+8: fora
    eventos.adicionar(Evento("passado", "2026-11-10", "10:00")) # evento passado: fora
    r = resumo_de_hoje(tarefas, eventos, HOJE)
    assert [a.nome for a in r["atrasadas"]] == ["atrasada"]
    assert [a.nome for a in r["hoje"]] == ["hoje", "reuniao"]
    assert [a.nome for a in r["proximos"]] == ["prova"]

def test_resumo_de_hoje_atravessa_ano(tarefas, eventos):
    eventos.adicionar(Evento("ano novo", "2027-01-01", "00:00"))
    assert [a.nome for a in resumo_de_hoje(tarefas, eventos, date(2026, 12, 28))["proximos"]] == ["ano novo"]

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
    assert all(d.weekday() == 6 for d in (s[0] for s in semanas))

def test_semanas_do_mes_sempre_6_semanas():
    for ano, mes in [(2026, 2), (2026, 11), (2027, 1)]:
        semanas = semanas_do_mes(ano, mes)
        assert len(semanas) == 6 and all(len(s) == 7 for s in semanas)

def test_titulos():
    assert titulo_do_dia(HOJE) == "Terça-feira, 17/11/2026"
    assert titulo_do_mes(2026, 3) == "Março 2026"
```

- [ ] **Step 2:** `python -m pytest tests/test_agenda.py -q`. Esperado: erro de import.
- [ ] **Step 3:** Implementar. `semanas_do_mes` usa `calendar.Calendar(firstweekday=6).monthdatescalendar(ano, mes)` e completa até 6 semanas acrescentando as semanas seguintes (`última + timedelta(days=7)`).
- [ ] **Step 4:** `python -m pytest -q`. Esperado: tudo PASS.
- [ ] **Step 5:** `git commit -m "Adiciona logica das visoes da agenda"`

---

### Task 3: Formulário de tarefa/evento (`app/gui/formulario.py`)

**Files:**
- Create: `app/gui/__init__.py` (vazio), `app/gui/formulario.py`
- Test: `tests/test_formulario.py`

**Interfaces:**
- Produces:
  - `montar_tarefa(nome: str, data_txt: str, original: Tarefa | None = None) -> Tarefa`: lança `ValueError` com a mensagem para a tela. Mensagens exatas: `"O nome não pode ficar vazio."`, `"Data inválida. Use DD/MM/AAAA (ex.: 20/11/2026)."`. Quando `original` existe, preserva `id` e `feito`.
  - `montar_evento(nome: str, data_txt: str, hora_txt: str, lembrete: bool, original: Evento | None = None) -> Evento`. Mensagem extra: `"Hora inválida. Use HH:MM (ex.: 14:30)."`
  - `class FormularioAtividade(tk.Toplevel)`: `__init__(self, pai, tipo: str, data_inicial: date, original=None, ao_salvar: Callable[[Tarefa | Evento], None])`. `tipo` é `"tarefa"` ou `"evento"`. É modal (`transient` + `grab_set`). Tem um `ttk.Label` de erro em vermelho. O botão Salvar chama `montar_*`. Se der `ValueError`, mostra a mensagem e não fecha. Senão, reescreve os campos no formato certo, chama `ao_salvar(obj)` e fecha. O Enter salva e o Esc cancela.

- [ ] **Step 1: Testes que falham**

```python
def test_montar_tarefa_conserta_data():
    assert montar_tarefa(" Estudar ", "20-11-26").data == "2026-11-20"

def test_montar_tarefa_rejeita_nome_vazio():
    with pytest.raises(ValueError, match="nome não pode ficar vazio"):
        montar_tarefa("  ", "20/11/2026")

def test_montar_tarefa_rejeita_data():
    with pytest.raises(ValueError, match="Data inválida"):
        montar_tarefa("Estudar", "31/02/2026")

def test_montar_tarefa_preserva_id_e_feito():
    original = Tarefa("Estudar", "2026-11-20", feito=True, id=7)
    t = montar_tarefa("Estudar mais", "21/11/2026", original)
    assert (t.id, t.feito, t.nome) == (7, True, "Estudar mais")

def test_montar_evento_conserta_hora_e_rejeita_invalida():
    assert montar_evento("Reunião", "20/11/2026", "14h", True).hora == "14:00"
    with pytest.raises(ValueError, match="Hora inválida"):
        montar_evento("Reunião", "20/11/2026", "25:00", False)
```

- [ ] **Step 2:** `python -m pytest tests/test_formulario.py -q`. Esperado: erro de import.
- [ ] **Step 3:** Implementar `montar_tarefa`/`montar_evento` (com `normalizar_data`/`normalizar_hora`) e `FormularioAtividade`. O campo data começa com `formatar_data_br(data_inicial ISO)` ou com a data de `original`.
- [ ] **Step 4:** `python -m pytest -q`. Esperado: tudo PASS.
- [ ] **Step 5:** `git commit -m "Adiciona formulario de tarefas e eventos"`

---

### Task 4: Lista reutilizável e as três abas

**Files:**
- Create: `app/gui/lista.py`, `app/gui/aba_hoje.py`, `app/gui/aba_calendario.py`, `app/gui/aba_todas.py`, `app/gui/janela.py`
- Modify: `main.py` (abrir janela; `--terminal` → menu antigo)
- Test: `tests/test_janela.py`

**Interfaces:**
- Consumes: Task 2 (todas as funções), Task 3 (`FormularioAtividade`).
- Produces:
  - `class ListaAtividades(ttk.Frame)` (`lista.py`): `__init__(self, pai, janela, mostrar_data: bool)`. Usa um `ttk.Treeview` com colunas `feito, tipo, data, hora, nome, info` (tipo = `"Tarefa"`/`"Evento"`). `mostrar(grupos: list[tuple[str | None, list]])` desenha os grupos: título `None` = sem cabeçalho, e cada título vira uma linha-pai aberta. O `iid` de cada atividade é `chave_item(a)` (cabeçalhos usam `"g0"`, `"g1"`…). Itens feitos usam a tag cinza. A data é exibida com `formatar_data_br`, e se falhar mostra o texto cru. Info mostra `"(ATRASADA)"` para tarefa atrasada e `"(lembrete)"` para evento com lembrete. Ações: Espaço ou clique na coluna feito → `janela.alternar_feito(chave)`. Duplo clique → `janela.editar(chave)`. Delete → `janela.remover(chave)`.
  - `class JanelaPrincipal(tk.Tk)` (`janela.py`): `__init__(self, conexao, hoje: Callable[[], date] = date.today)`. Título `"Task & Events Manager"`, geometria `800x600`. Tem um `ttk.Notebook` com as abas `"Hoje"`, `"Calendário"` e `"Todas"`, nessa ordem, e a selecionada inicialmente é Hoje. Métodos:
    - `atualizar_tudo()` chama `atualizar()` de cada aba.
    - `buscar(chave: str)` → `Tarefa | Evento | None` usa o prefixo `t`/`e`.
    - `alternar_feito(chave)`, `editar(chave)`, `remover(chave)` (com `messagebox.askyesno("Remover", f"Remover '{nome}'?")`) e `nova(tipo: str, dia: date)` usam o repositório e chamam `atualizar_tudo()`.
    - `ValueError` do repositório vira `messagebox.showerror`.
  - Cada aba é `ttk.Frame` com `atualizar()`:
    - `AbaHoje`: título `titulo_do_dia(hoje)`, botões `+ Tarefa`/`+ Evento` (dia = hoje) e uma `ListaAtividades(mostrar_data=True)` com os grupos `"ATRASADAS"`, `"HOJE"` e `"PRÓXIMOS 7 DIAS"`. Grupo vazio não aparece. Se os três estiverem vazios, mostra a mensagem `"Nada para hoje. Use + Tarefa ou + Evento."`.
    - `AbaCalendario`: tem `◀`, `titulo_do_mes`, `▶` e `Hoje`, mais uma grade 6×7 de `tk.Button` com cabeçalho `CABECALHO_SEMANA`. O dia com atividade fica em negrito com fundo `#dbeafe`. Hoje tem borda `relief="solid"`. O dia selecionado tem fundo `#93c5fd`. Os dias de fora do mês ficam com texto cinza `#9ca3af`. Embaixo vai o `titulo_do_dia(selecionado)`, os botões `+` (dia = selecionado) e uma `ListaAtividades(mostrar_data=False)` com um grupo `None`.
    - `AbaTodas`: `ListaAtividades(mostrar_data=True)` com um grupo `None` de `todas_atividades`.
  - `main.py`: `main()` abre `JanelaPrincipal(criar_conexao())` e chama `mainloop()`. Com `"--terminal" in sys.argv`, roda o menu atual, renomeado para `main_terminal()`. As funções `perguntar_*`/`adicionar_*` atuais continuam lá (os testes de `test_main.py` não mudam).

- [ ] **Step 1: Teste de fumaça que falha**

```python
def test_janela_abre_na_aba_hoje_e_mostra_tarefa(conexao):
    TarefaRepository(conexao).adicionar(Tarefa("Estudar", "2026-11-17"))
    janela = JanelaPrincipal(conexao, hoje=lambda: date(2026, 11, 17))
    janela.withdraw()
    try:
        assert janela.notebook.tab(janela.notebook.select(), "text") == "Hoje"
        assert janela.aba_hoje.lista.tree.exists("t1")
        janela.alternar_feito("t1")
        assert TarefaRepository(conexao).buscar_por_id(1).feito is True
        assert janela.aba_calendario.lista.tree.exists("t1")
    finally:
        janela.destroy()
```

- [ ] **Step 2:** `python -m pytest tests/test_janela.py -q`. Esperado: erro de import.
- [ ] **Step 3:** Implementar `lista.py`, as três abas, `janela.py` e a mudança no `main.py`, conforme Interfaces.
- [ ] **Step 4:** `python -m pytest -q`. Esperado: tudo PASS.
- [ ] **Step 5: Verificação manual:** `python main.py` numa pasta temporária. Testar: adicionar tarefa com data `20-11-26` (o campo vira `20/11/2026`), hora `25:00` (erro vermelho, formulário aberto), duplo clique para editar, Espaço para marcar, Delete para remover, ◀ ▶ no calendário e clique num dia destacado. Depois, `python main.py --terminal` abre o menu antigo.
- [ ] **Step 6:** `git commit -m "Adiciona interface grafica com abas Hoje, Calendario e Todas"`

---

### Task 5: Documentação

**Files:**
- Modify: `README.md`

- [ ] **Step 1:** Marcar no README "Interface gráfica", "Visualização em calendário" (com a observação "mês; semana em breve") e "Destaque dos dias" como feitos. Atualizar a seção "Como executar" (`python main.py` abre a janela; `--terminal`) e a estrutura (`app/agenda.py`, `app/gui/`, `docs/`). Adicionar em "Em desenvolvimento": visão de semana e lembretes em segundo plano (7/14/21 dias).
- [ ] **Step 2:** `python -m pytest -q`. Esperado: tudo PASS.
- [ ] **Step 3:** `git add docs README.md` e `git commit -m "Atualiza README e adiciona design e plano da interface"`
