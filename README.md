# Task-Events-Manager

Aplicativo desktop em Python para gerenciar **tarefas** e **eventos**, centralizando a rotina pessoal e os compromissos futuros em um só lugar, com visualização em calendário.

> **Status: em desenvolvimento.** A interface gráfica (abas Hoje, Calendário e Todas), a camada de dados e as regras de negócio já estão prontas e testadas.

## Sobre o projeto

Permite cadastrar tarefas que precisam ser feitas em determinado dia e registrar eventos futuros (reuniões, aniversários, compromissos), facilitando a visualização e o gerenciamento da agenda.

## Funcionalidades

**Já implementado**
- [x] Cadastro, listagem, edição e exclusão de tarefas
- [x] Cadastro, listagem, edição e exclusão de eventos (data, horário e lembrete)
- [x] Marcar tarefas e eventos como concluídos
- [x] Validação de nome, data (DD/MM/AAAA) e hora (HH:MM), com correção automática de formatos comuns
- [x] Detecção de tarefas atrasadas e contagem de dias restantes para um evento
- [x] Interface gráfica (Tkinter) que abre mostrando o dia de hoje: atrasadas, hoje e próximos 7 dias
- [x] Visualização em calendário mensal
- [x] Destaque dos dias com atividades cadastradas
- [x] Testes automatizados com pytest

**Em desenvolvimento**
- [ ] Visualização da semana no calendário
- [ ] Lembretes com o app rodando em segundo plano (avisos a cada 7, 14 ou 21 dias, conforme a escolha do usuário)

## Tecnologias

- Python 3
- Tkinter (interface gráfica, já vem com o Python)
- SQLite3 (módulo `sqlite3` da biblioteca padrão)
- pytest

## Estrutura do projeto

```
Task-Events-Manager/
├── app/
│   ├── models.py          # Tarefa e Evento (regras e validações)
│   ├── database.py        # conexão e criação das tabelas
│   ├── repositories.py    # acesso ao banco (SQL)
│   ├── agenda.py          # o que cada visão mostra (hoje, mês, dia)
│   └── gui/               # janela Tkinter: abas, lista e formulário
├── docs/                  # design e planos de implementação
├── tests/                 # testes automatizados
├── main.py                # abre a janela (ou o menu com --terminal)
├── pytest.ini
└── README.md
```

A separação em camadas mantém o SQL isolado em `repositories.py`, as regras em `models.py` e os cálculos das visões em `agenda.py`. A pasta `gui/` só desenha a tela, por isso quase tudo é testado com um banco em memória, sem abrir janela.

## Como executar

```bash
python main.py              # abre a janela
python main.py --terminal   # abre o menu no terminal
```

A janela abre na aba **Hoje**. Na aba **Calendário**, clique num dia para ver as atividades dele. Nas listas, Espaço marca/desmarca como feito, duplo clique edita e Delete remove. Os dados ficam salvos em `dados.db`. As datas são exibidas no padrão brasileiro (DD/MM/AAAA). Também é possível digitar `20-11-2026`, `20/11/26` ou `20112026`, que o programa converte. Horas podem ser digitadas como `14:30`, `14h30` ou `14h`.

Internamente o banco guarda a data como AAAA-MM-DD, porque nesse formato a ordenação por texto coincide com a ordem cronológica.

## Como executar os testes

```bash
git clone https://github.com/ramonnees/Task-Events-Manager.git
cd Task-Events-Manager
pip install pytest
pytest
```

## Autor

Ramon Felipe Schuck Mielke · [LinkedIn](https://www.linkedin.com/in/ramon-mielke-937985208) · [GitHub](https://github.com/ramonnees)
