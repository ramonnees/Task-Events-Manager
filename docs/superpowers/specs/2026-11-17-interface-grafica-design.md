# Interface gráfica (Tkinter): design

Data: 17/11/2026

## Intenção

Hoje o Task-Events-Manager só tem um menu no terminal. O objetivo é uma janela desktop
em Tkinter que **abre mostrando o dia de hoje** (o que fazer agora) e deixa a pessoa
**trocar para uma visão de calendário** quando quiser ver a semana ou o mês. Isso cobre os
três itens "Em desenvolvimento" do README: interface gráfica, calendário e destaque dos
dias com atividades.

## Objetivos

- Abrir na aba **Hoje**, com tarefas atrasadas, as atividades de hoje e as dos próximos dias.
- Aba **Calendário**: o mês em grade, com os dias que têm atividades destacados. Clicar
  num dia mostra as atividades dele.
- Aba **Todas**: lista completa de tarefas e eventos.
- Adicionar, editar, marcar/desmarcar como feito e remover tarefas e eventos pela janela.
- Datas sempre em DD/MM/AAAA. Os erros de digitação usam o mesmo conserto/aviso do terminal.

## Fora do escopo (agora)

- Visão de **semana** no calendário (o README pede; fica para um próximo passo, numa
  aba ou modo novo, sem mexer nas outras abas).
- Notificação de lembrete (pop-up/som). O lembrete continua sendo só uma marcação.
  **Desejo do Ramon para o futuro:** o app fica rodando em segundo plano, mesmo com a
  janela fechada (ex.: ícone perto do relógio do Windows), e avisa a cada 7, 14 ou 21 dias,
  conforme a escolha do usuário. A esclarecer quando for implementado: se é "repetir o aviso
  a cada N dias" ou "avisar N dias antes do evento". Isso deve transformar o `lembrete`
  (hoje sim/não) em um número de dias, o que exige mudar a tabela `eventos`.
- Filtros e busca na aba Todas.
- Configuração de qual aba abre primeiro. Sempre abre em Hoje.

## Anti-objetivos

- A interface **não** pode ter SQL nem regras de negócio. Tudo passa por
  `app/models.py` e `app/repositories.py`.
- Não pode gravar dados inválidos. O repositório já bloqueia, e a janela deve mostrar o
  erro e manter o formulário aberto para corrigir, nunca fechar perdendo o que foi digitado.
- Não pode exigir instalar nada além do Python (Tkinter já vem junto).

## Restrições

- Python 3.13, Tkinter 8.6 (`tkinter` + `tkinter.ttk`), SQLite já existente.
- O banco guarda datas em AAAA-MM-DD (ordenação). A tela mostra DD/MM/AAAA.
- Todo código novo de lógica precisa de teste com pytest (padrão do projeto).

## Abordagens consideradas

1. **Abas (escolhida).** Abas Hoje / Calendário / Todas. Cada visão ocupa a janela
   inteira, é independente das outras e a de semana entra depois sem mexer no resto.
2. **Calendário e lista lado a lado.** Mostra tudo de uma vez, mas não deixa escolher a
   visão, a lista fica apertada e a semana não cabe bem.
3. **Botões Dia/Semana/Mês (estilo Google Agenda).** A mais completa, mas a visão de
   semana com horários é trabalhosa demais para o primeiro passo.

Escolha do Ramon: **abordagem 1**, porque abre no dia de hoje e permite escolher a visão.

## Como fica

### Aba Hoje (abre primeiro)

```
Terça-feira, 17/11/2026                        [+ Tarefa] [+ Evento]
ATRASADAS
  [ ]        15/11  Pagar boleto
HOJE
  [ ]               Estudar SQL
  [ ]  14:30        Reunião  (lembrete)
PRÓXIMOS 7 DIAS
  [ ]  10:00  20/11  Prova
```

- **Atrasadas**: tarefas não feitas com data anterior a hoje (regra de `Tarefa.atrasada`).
  Eventos passados não entram, porque evento que já passou não está "atrasado".
- **Hoje**: tarefas e eventos com a data de hoje (feitos aparecem marcados).
- **Próximos 7 dias**: de amanhã até hoje+7.
- Dentro de cada grupo: ordem por data, depois hora (tarefas sem hora vêm antes dos eventos do dia).

### Aba Calendário

```
   ◀  Novembro 2026  ▶      [Hoje]
 Dom Seg Ter Qua Qui Sex Sáb
   1   2   3   4   5   6   7
  ...         [17] ...  20•
------------------------------
Sexta-feira, 20/11/2026     [+ Tarefa] [+ Evento]
  [ ]  10:00  Prova
```

- Grade de 6 semanas × 7 dias, **semana começando no domingo**.
- Dias com atividade: destacados (negrito/cor). Hoje: com contorno. Dia selecionado: fundo.
- Dias de outros meses aparecem apagados.
- ◀ ▶ trocam o mês; [Hoje] volta para o mês atual e seleciona hoje.
- Abaixo da grade, a lista do dia selecionado (começa em hoje). Os botões "+" já vêm com
  a data do dia selecionado preenchida.

### Aba Todas

Uma lista com todas as tarefas e eventos ordenados por data e hora. As colunas são:
feito, tipo (Tarefa/Evento), data, hora, nome e lembrete.

### Ações (iguais nas três abas)

- **Marcar/desmarcar como feito**: clique na coluna `[ ]` ou tecla Espaço.
- **Editar**: duplo clique abre o formulário preenchido.
- **Remover**: tecla Delete ou botão, com confirmação ("Remover 'Prova'?").
- Itens já feitos continuam aparecendo em todas as listas, marcados `[x]` e em cinza.
- Tarefa e evento podem ter o mesmo id no banco, por isso cada linha da lista guarda o
  tipo junto com o id (ex.: `t3`, `e3`).
- Depois de qualquer mudança, **todas as abas são atualizadas**.

### Formulário (janela pequena, modal)

- Tarefa: Nome, Data. Evento: Nome, Data, Hora, Lembrete (caixa de marcar).
- Data inicial: hoje, ou o dia selecionado no calendário.
- Ao salvar: usa `normalizar_data`/`normalizar_hora`. Se não der para entender, mostra a
  mensagem em vermelho no próprio formulário e **não fecha**. Se precisou consertar, o
  campo é reescrito no formato certo (ex.: `20-11-26` vira `20/11/2026`).
- Nome vazio: mensagem "O nome não pode ficar vazio".

## Estrutura do código

```
app/
  agenda.py          # NOVO: lógica das visões, sem Tkinter (testável)
  repositories.py    # + listar_por_periodo(inicio, fim) nas duas classes
                     # + TarefaRepository.listar_atrasadas(hoje)
  gui/               # NOVO: só Tkinter, sem regra de negócio
    janela.py        # janela principal, abas, atualizar tudo
    aba_hoje.py
    aba_calendario.py
    aba_todas.py
    lista.py         # lista reutilizada nas 3 abas (Treeview + ações)
    formulario.py    # formulários de tarefa e evento
main.py              # passa a abrir a janela; `python main.py --terminal` abre o menu antigo
```

`app/agenda.py` concentra o que a tela precisa calcular, para ser testado sem abrir janela:
- `resumo_de_hoje(tarefas_repo, eventos_repo, hoje)` → grupos atrasadas / hoje / próximos.
- `atividades_do_dia(..., dia)` → lista do dia, já ordenada.
- `dias_com_atividades(..., ano, mes)` → conjunto de dias para destacar.
- `semanas_do_mes(ano, mes)` → a grade 6×7 de datas (semana começando no domingo).
- Nomes de dias e meses em português fixos no código (não depender do `locale` do Windows).

## Testes

- `listar_por_periodo` e `listar_atrasadas`: testes no banco em memória (como os atuais).
- `app/agenda.py`: testes com data fixa (`hoje = date(2026, 11, 17)`), incluindo virada de
  mês, mês que começa no domingo e fevereiro.
- Interface: um teste de fumaça que cria a janela com banco em memória, sem mostrá-la
  (`withdraw`), e fecha. O resto da interface é verificado rodando o programa.

## Decisões tomadas por mim (Claude), aprovadas pelo Ramon em 17/11/2026

- Semana do calendário começa no **domingo** (padrão dos calendários brasileiros).
- "Próximos dias" = **7 dias**.
- Eventos passados não contam como atrasados.
- **Editar** entra agora, mesmo não estando no menu do terminal, porque o repositório já suporta.
- `main.py` abre a janela por padrão, e o menu do terminal continua disponível com `--terminal`.
- Visual: `ttk` com o tema padrão do Windows, sem bibliotecas extras.

## Fica a critério de quem implementar

- Cores e fontes exatas do destaque no calendário.
- Tamanho inicial da janela (sugestão: 800×600, redimensionável).
- Atalhos de teclado além de Espaço, Delete e duplo clique.
