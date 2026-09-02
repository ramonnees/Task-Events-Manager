class Tarefa:
    def __init__(self, nome, data, feito=False, id = None):
        self.id = id
        self.nome = nome
        self.data = data
        self.feito = feito

    def __repr__(self):
        return f"Tarefa: {self.nome}, Data: {self.data}, Feito: {self.feito}"
    
    def marcar_como_feito(self):
        self.feito = True
    def marcar_como_nao_feito(self):
        self.feito = False

    def eh_valido(self):
        """Verifica se a tarefa é valida(nome e data nao podem ser vazios)"""
        return bool(self.nome.strip()) and bool(self.data.strip())

    #def atrasada(self):

class Evento:
    def __init__(self, nome, data, hora, lembrete, feito=False, id=None):
        self.id = id
        self.nome = nome
        self.data = data
        self.hora = hora
        self.lembrete = lembrete
        self.feito = feito

    def __repr__(self):
        return f"Evento: {self.nome}, Data: {self.data}, Hora: {self.hora}, Lembrete: {self.lembrete}, Feito: {self.feito}"
    
    def marcar_como_feito(self):
        self.feito = True
    
    def marcar_como_nao_feito(self):
        self.feito = False
    
   #def dias_restantes(self):
