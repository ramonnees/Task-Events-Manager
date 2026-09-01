import sqlite3 

def criar_conexao():
    conexao = sqlite3.connect('dados.db')
    return conexao

def criar_tabelas():
    """Cria a tabela de tarefas, caso ela ainda nao exista."""
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data TEXT,
            feito BOOLEAN
        )
    """)
    """Cria a tabela de eventos, caso ela ainda nao exista."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data TEXT,
            hora TEXT,
            lembrete BOOLEAN
            feito BOOLEAN
        )
    """)
    conexao.commit()
    conexao.close()