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

def adicionar_tarefa(nome, data, feito):
    """Adiciona uma nova tarefa no banco de dados"""
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO tarefas (nome, data, feito) VALUES (?, ?, ?)", (nome, data, feito))
    conexao.commit()
    conexao.close()
    return True

def adicionar_evento(nome, data, hora, lembrete, feito):
    """Adiciona um novo evento no banco de dados"""
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO eventos (nome, data, hora, lembrete, feito) VALUES (?, ?, ?, ?, ?)", (nome, data, hora, lembrete, feito))
    conexao.commit()
    conexao.close()
    return True

def listar_tarefas():
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM tarefas")
    tarefas = cursor.fetchall()
    conexao.close()
    return tarefas

def listar_eventos():
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM eventos")
    eventos = cursor.fetchall()
    conexao.close()
    return eventos

def marcar_tarefa_feita(id):
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("UPDATE tarefas SET feito = 1 WHERE id = ?",(id,))
    conexao.commit()
    conexao.close()
    return True

def remover_tarefa(id):
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    return True

def remover_evento(id):
    conexao = criar_conexao()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM eventos WHERE id = ?", (id,))
    conexao.commit()
    conexao.close()
    return True

