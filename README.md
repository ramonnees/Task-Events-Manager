# Task-Events-Manager

Aplicativo desktop em Python para gerenciar **tarefas** e **eventos**, centralizando a rotina pessoal e os compromissos futuros em um só lugar, com visualização em calendário.

> **Status: em desenvolvimento.** A camada de dados e as regras de negócio já estão prontas e testadas. A interface gráfica e o calendário estão em construção.

## Sobre o projeto

Permite cadastrar tarefas que precisam ser feitas em determinado dia e registrar eventos futuros (reuniões, aniversários, compromissos), facilitando a visualização e o gerenciamento da agenda.

## Funcionalidades

**Já implementado (camada de dados e regras)**
- [x] Cadastro, listagem, edição e exclusão de tarefas
- [x] Cadastro, listagem, edição e exclusão de eventos (data, horário e lembrete)
- [x] Marcar tarefas e eventos como concluídos
- [x] Validação de nome, data (DD/MM/AAAA) e hora (HH:MM), com correção automática de formatos comuns
- [x] Detecção de tarefas atrasadas e contagem de dias restantes para um evento
- [x] Testes automatizados com pytest

**Em desenvolvimento**
- [ ] Interface gráfica
- [ ] Visualização em calendário (dias, semanas e meses)
- [ ] Destaque dos dias com atividades cadastradas

## Tecnologias

- Python 3
- SQLite3 (módulo `sqlite3` da biblioteca padrão)
- pytest

## Estrutura do projeto

```
Task-Events-Manager/
├── app/
│   ├── models.py          # Tarefa e Evento (regras e validações)
│   ├── database.py        # conexão e criação das tabelas
│   └── repositories.py    # acesso ao banco (SQL)
├── tests/                 # testes automatizados
├── main.py                # menu no terminal
├── pytest.ini
└── README.md
```

A separação em camadas mantém o SQL isolado em `repositories.py` e as regras em `models.py`, o que permite testar tudo com um banco em memória, sem interface.

## Como executar

```bash
python main.py
```

Abre um menu no terminal. Os dados ficam salvos em `dados.db`. As datas são exibidas no padrão brasileiro (DD/MM/AAAA). Também é possível digitar `20-11-2026`, `20/11/26` ou `20112026`, que o programa converte. Horas podem ser digitadas como `14:30`, `14h30` ou `14h`.

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
