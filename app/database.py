import sqlite3

CAMINHO_PADRAO = "dados.db"


def criar_conexao(caminho=CAMINHO_PADRAO):
    """Abre uma conexão. Nos testes, use caminho=':memory:'."""
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row   # acessar colunas por nome: linha["nome"]
    return conexao


def criar_tabelas(conexao):
    """Cria as tabelas, caso ainda não existam."""
    with conexao:   # commit automático (ou rollback se der erro)
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data TEXT NOT NULL,
                feito INTEGER NOT NULL DEFAULT 0
            )
        """)
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data TEXT NOT NULL,
                hora TEXT NOT NULL,
                lembrete INTEGER NOT NULL DEFAULT 0,
                feito INTEGER NOT NULL DEFAULT 0
            )
        """)
