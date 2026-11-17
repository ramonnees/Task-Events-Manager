import pytest
from app.database import criar_conexao, criar_tabelas
from app.repositories import TarefaRepository, EventoRepository


@pytest.fixture
def conexao():
    conexao = criar_conexao(":memory:")   # banco novo e vazio a cada teste
    criar_tabelas(conexao)
    yield conexao
    conexao.close()


@pytest.fixture
def tarefas(conexao):
    return TarefaRepository(conexao)


@pytest.fixture
def eventos(conexao):
    return EventoRepository(conexao)
