from datetime import date, datetime

# Formato guardado no banco. Fica em AAAA-MM-DD porque, como texto, ele ordena
# na ordem cronológica (ORDER BY data). Em DD/MM/AAAA, "01/12" viria antes de "20/11".
FORMATO_DATA = "%Y-%m-%d"      # ex.: 2026-11-20
# Formato que a pessoa vê e digita.
FORMATO_DATA_BR = "%d/%m/%Y"   # ex.: 20/11/2026
FORMATO_HORA = "%H:%M"         # ex.: 14:30


def formatar_data_br(data_iso):
    """'2026-11-20' -> '20/11/2026'."""
    return datetime.strptime(data_iso, FORMATO_DATA).strftime(FORMATO_DATA_BR)


def _data_valida(texto):
    try:
        datetime.strptime(texto, FORMATO_DATA)
        return True
    except (TypeError, ValueError):
        return False


def _hora_valida(texto):
    try:
        datetime.strptime(texto, FORMATO_HORA)
        return True
    except (TypeError, ValueError):
        return False


# Formatos que a pessoa costuma digitar. A ordem importa: os de ano com 4 dígitos
# vêm antes, para "20/11/2026" não ser lido como ano de 2 dígitos.
_FORMATOS_DATA_ACEITOS = [
    "%d/%m/%Y",   # 20/11/2026 (padrão)
    "%Y-%m-%d",   # 2026-11-20
    "%d-%m-%Y",   # 20-11-2026
    "%d.%m.%Y",   # 20.11.2026
    "%Y/%m/%d",   # 2026/11/20
    "%d%m%Y",     # 20112026
    "%d/%m/%y",   # 20/11/26
    "%d-%m-%y",   # 20-11-26
]

_FORMATOS_HORA_ACEITOS = [
    "%H:%M",      # 14:30 (também aceita 9:05)
    "%H",         # 14 (vira 14:00). Precisa vir antes de %H%M, senão "14" vira 01:04
    "%H%M",       # 1430 ou 930
]


def normalizar_data(texto):
    """Tenta consertar a data digitada e devolve no formato do banco (AAAA-MM-DD).

    Devolve None quando não dá para entender a data (ex.: '31/02/2026', 'abc').
    """
    if not texto or not texto.strip():
        return None
    texto = texto.strip()
    for formato in _FORMATOS_DATA_ACEITOS:
        try:
            return datetime.strptime(texto, formato).strftime(FORMATO_DATA)
        except ValueError:
            continue
    return None


def normalizar_hora(texto):
    """Tenta consertar a hora digitada e devolve no formato HH:MM.

    Aceita '14:30', '14h30', '14h', '1430', '9:05'. Devolve None se não der.
    """
    if not texto or not texto.strip():
        return None
    texto = texto.strip().lower().replace("h", ":").rstrip(":")
    for formato in _FORMATOS_HORA_ACEITOS:
        try:
            return datetime.strptime(texto, formato).strftime(FORMATO_HORA)
        except ValueError:
            continue
    return None


class Tarefa:
    def __init__(self, nome, data, feito=False, id=None):
        self.id = id
        self.nome = nome
        self.data = data
        self.feito = bool(feito)

    def __repr__(self):
        return f"Tarefa: {self.nome}, Data: {self._data_para_exibir()}, Feito: {self.feito}"

    @property
    def data_br(self):
        """Data no padrão brasileiro (DD/MM/AAAA), para mostrar na tela."""
        return formatar_data_br(self.data)

    def _data_para_exibir(self):
        # repr não pode quebrar com data inválida, então mostra como veio
        return self.data_br if _data_valida(self.data) else self.data

    def marcar_como_feito(self):
        self.feito = True

    def marcar_como_nao_feito(self):
        self.feito = False

    def eh_valido(self):
        """Nome não pode ser vazio e a data precisa estar no formato AAAA-MM-DD."""
        return bool(self.nome and self.nome.strip()) and _data_valida(self.data)

    def atrasada(self, hoje=None):
        """True se a tarefa não foi feita e a data já passou."""
        hoje = hoje or date.today()
        data = datetime.strptime(self.data, FORMATO_DATA).date()
        return not self.feito and data < hoje


class Evento:
    def __init__(self, nome, data, hora, lembrete=False, feito=False, id=None):
        self.id = id
        self.nome = nome
        self.data = data
        self.hora = hora
        self.lembrete = bool(lembrete)
        self.feito = bool(feito)

    def __repr__(self):
        return (f"Evento: {self.nome}, Data: {self._data_para_exibir()}, Hora: {self.hora}, "
                f"Lembrete: {self.lembrete}, Feito: {self.feito}")

    @property
    def data_br(self):
        """Data no padrão brasileiro (DD/MM/AAAA), para mostrar na tela."""
        return formatar_data_br(self.data)

    def _data_para_exibir(self):
        return self.data_br if _data_valida(self.data) else self.data

    def marcar_como_feito(self):
        self.feito = True

    def marcar_como_nao_feito(self):
        self.feito = False

    def eh_valido(self):
        return (bool(self.nome and self.nome.strip())
                and _data_valida(self.data) and _hora_valida(self.hora))

    def dias_restantes(self, hoje=None):
        """Dias até o evento (negativo se já passou)."""
        hoje = hoje or date.today()
        data = datetime.strptime(self.data, FORMATO_DATA).date()
        return (data - hoje).days
