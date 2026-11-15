class Produto:
    __proximoCodigo = 1

    def __init__(self, nome, categoria, preco, quantidade):
        self.__codigo = Produto.__proximoCodigo
        Produto.__proximoCodigo += 1
        self.__nome = nome
        self.__categoria = categoria
        self.__preco = preco if preco > 0 else 0.0
        self.__quantidade = quantidade if quantidade >= 0 else 0

    @property
    def codigo(self):
        return self.__codigo

    @property
    def nome(self):
        return self.__nome

    @property
    def categoria(self):
        return self.__categoria

    @property
    def preco(self):
        return self.__preco

    @property
    def quantidade(self):
        return self.__quantidade

    def set_preco(self, novoPreco):
        if novoPreco <= 0:
            return False
        self.__preco = novoPreco
        return True

    def adicionar_estoque(self, unidades):
        if unidades <= 0:
            return False
        self.__quantidade += unidades
        return True

    def remover_estoque(self, unidades):
        if unidades <= 0 or unidades > self.__quantidade:
            return False
        self.__quantidade -= unidades
        return True

    def valor_em_estoque(self):
        return self.__preco * self.__quantidade

    def estoque_baixo(self, limite):
        return self.__quantidade < limite
