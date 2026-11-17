from app.models import Evento, Tarefa


def _garantir_valido(objeto):
    """Última barreira antes do banco: nunca grava tarefa/evento inválido."""
    if not objeto.eh_valido():
        raise ValueError(f"Dados inválidos, nada foi gravado: {objeto!r}")


class TarefaRepository:
    def __init__(self, conexao):
        self.conexao = conexao

    @staticmethod
    def _para_objeto(linha):
        return Tarefa(linha["nome"], linha["data"], bool(linha["feito"]), linha["id"])

    def adicionar(self, tarefa):
        _garantir_valido(tarefa)
        with self.conexao:
            cursor = self.conexao.execute(
                "INSERT INTO tarefas (nome, data, feito) VALUES (?, ?, ?)",
                (tarefa.nome.strip(), tarefa.data, int(tarefa.feito)),
            )
        tarefa.id = cursor.lastrowid
        return tarefa

    def listar(self):
        linhas = self.conexao.execute("SELECT * FROM tarefas ORDER BY data, id").fetchall()
        return [self._para_objeto(l) for l in linhas]

    def listar_por_periodo(self, inicio, fim):
        """Tarefas com data entre inicio e fim (AAAA-MM-DD, inclusive)."""
        linhas = self.conexao.execute(
            "SELECT * FROM tarefas WHERE data BETWEEN ? AND ? ORDER BY data, id",
            (inicio, fim),
        ).fetchall()
        return [self._para_objeto(l) for l in linhas]

    def listar_atrasadas(self, hoje):
        """Tarefas não feitas com data anterior a hoje (AAAA-MM-DD)."""
        linhas = self.conexao.execute(
            "SELECT * FROM tarefas WHERE feito = 0 AND data < ? ORDER BY data, id",
            (hoje,),
        ).fetchall()
        return [self._para_objeto(l) for l in linhas]

    def buscar_por_id(self, id):
        linha = self.conexao.execute("SELECT * FROM tarefas WHERE id = ?", (id,)).fetchone()
        return self._para_objeto(linha) if linha else None

    def atualizar(self, tarefa):
        _garantir_valido(tarefa)
        with self.conexao:
            cursor = self.conexao.execute(
                "UPDATE tarefas SET nome = ?, data = ?, feito = ? WHERE id = ?",
                (tarefa.nome.strip(), tarefa.data, int(tarefa.feito), tarefa.id),
            )
        return cursor.rowcount > 0   # False se o id não existe

    def remover(self, id):
        with self.conexao:
            cursor = self.conexao.execute("DELETE FROM tarefas WHERE id = ?", (id,))
        return cursor.rowcount > 0


class EventoRepository:
    def __init__(self, conexao):
        self.conexao = conexao

    @staticmethod
    def _para_objeto(linha):
        return Evento(linha["nome"], linha["data"], linha["hora"],
                      bool(linha["lembrete"]), bool(linha["feito"]), linha["id"])

    def adicionar(self, evento):
        _garantir_valido(evento)
        with self.conexao:
            cursor = self.conexao.execute(
                "INSERT INTO eventos (nome, data, hora, lembrete, feito) VALUES (?, ?, ?, ?, ?)",
                (evento.nome.strip(), evento.data, evento.hora,
                 int(evento.lembrete), int(evento.feito)),
            )
        evento.id = cursor.lastrowid
        return evento

    def listar(self):
        linhas = self.conexao.execute("SELECT * FROM eventos ORDER BY data, hora, id").fetchall()
        return [self._para_objeto(l) for l in linhas]

    def listar_por_periodo(self, inicio, fim):
        """Eventos com data entre inicio e fim (AAAA-MM-DD, inclusive)."""
        linhas = self.conexao.execute(
            "SELECT * FROM eventos WHERE data BETWEEN ? AND ? ORDER BY data, hora, id",
            (inicio, fim),
        ).fetchall()
        return [self._para_objeto(l) for l in linhas]

    def buscar_por_id(self, id):
        linha = self.conexao.execute("SELECT * FROM eventos WHERE id = ?", (id,)).fetchone()
        return self._para_objeto(linha) if linha else None

    def atualizar(self, evento):
        _garantir_valido(evento)
        with self.conexao:
            cursor = self.conexao.execute(
                "UPDATE eventos SET nome = ?, data = ?, hora = ?, lembrete = ?, feito = ? WHERE id = ?",
                (evento.nome.strip(), evento.data, evento.hora,
                 int(evento.lembrete), int(evento.feito), evento.id),
            )
        return cursor.rowcount > 0

    def remover(self, id):
        with self.conexao:
            cursor = self.conexao.execute("DELETE FROM eventos WHERE id = ?", (id,))
        return cursor.rowcount > 0
