from padaria.produto import Produto


def moeda(valor):
    """Formata como R$ 1.234,56."""
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


class Padaria:
    MAX_PRODUTOS = 20
    LIMITE_ESTOQUE_BAIXO = 5
    DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    def __init__(self, nome):
        self._nome = nome
        self._produtos = []
        self._historico = []
        # Linha = posição do produto na lista; coluna = dia - 1.
        self._vendas = [[0] * 7 for _ in range(Padaria.MAX_PRODUTOS)]
        self._faturamento_por_dia = [0.0] * 7

    @property
    def nome(self):
        return self._nome

    # ---------- Cadastro e buscas ----------
    def cadastrar_produto(self, nome, categoria, preco, quantidade):
        nome = (nome or "").strip()
        if not nome:
            return "ERRO: o nome não pode ficar vazio."
        if self._existe_produto_com_nome(nome):
            return f"ERRO: já existe um produto chamado {nome}."
        if preco <= 0:
            return "ERRO: o preço deve ser maior que zero."
        if quantidade < 0:
            return "ERRO: a quantidade inicial não pode ser negativa."
        if len(self._produtos) >= Padaria.MAX_PRODUTOS:
            return f"ERRO: limite de {Padaria.MAX_PRODUTOS} produtos atingido."
        categoria = (categoria or "").strip() or "Sem categoria"
        # Só cria o Produto depois de validar tudo, para não gastar um código.
        p = Produto(nome, categoria, preco, quantidade)
        self._produtos.append(p)
        self._registrar_no_historico(f"Cadastro: {p.nome} (código {p.codigo})")
        return f"OK: produto cadastrado com o código {p.codigo}."

    def buscar_por_codigo(self, codigo):
        i = self._indice_do_produto(codigo)
        return None if i == -1 else self._produtos[i]

    def buscar_por_nome(self, trecho):
        busca = trecho.strip().lower()
        return [p for p in self._produtos if busca in p.nome.lower()]

    def get_produtos(self):
        """Devolve uma CÓPIA da lista."""
        return list(self._produtos)

    def get_quantidade_de_produtos(self):
        return len(self._produtos)

    # ---------- Operações ----------
    def registrar_venda(self, codigo, unidades, dia):
        # Valida tudo antes de alterar qualquer dado.
        pos = self._indice_do_produto(codigo)
        if pos == -1:
            return f"ERRO: produto de código {codigo} não encontrado."
        if unidades <= 0:
            return "ERRO: a quantidade deve ser maior que zero."
        if not self._dia_valido(dia):
            return "ERRO: dia inválido. Use de 1 (Seg) a 7 (Dom)."
        p = self._produtos[pos]
        if unidades > p.quantidade:
            return f"ERRO: estoque insuficiente. Disponível: {p.quantidade} unidade(s)."
        p.remover_estoque(unidades)
        total = unidades * p.preco  # valor guardado na hora da venda
        self._vendas[pos][dia - 1] += unidades  # dia 1..7 -> coluna 0..6
        self._faturamento_por_dia[dia - 1] += total
        self._registrar_no_historico(
            f"Venda: {unidades} x {p.nome} ({Padaria.DIAS[dia - 1]}) = {moeda(total)}"
        )
        return (f"OK: venda registrada. Total: {moeda(total)}. "
                f"Estoque restante: {p.quantidade}.")

    def repor_estoque(self, codigo, unidades):
        p = self.buscar_por_codigo(codigo)
        if p is None:
            return f"ERRO: produto de código {codigo} não encontrado."
        if not p.adicionar_estoque(unidades):
            return "ERRO: a quantidade deve ser maior que zero."
        self._registrar_no_historico(f"Reposição: {unidades} x {p.nome}")
        return f"OK: estoque de {p.nome} agora é {p.quantidade}."

    def alterar_preco(self, codigo, novo_preco):
        p = self.buscar_por_codigo(codigo)
        if p is None:
            return f"ERRO: produto de código {codigo} não encontrado."
        antigo = p.preco
        if not p.set_preco(novo_preco):
            return "ERRO: o preço deve ser maior que zero."
        self._registrar_no_historico(
            f"Preço de {p.nome}: {moeda(antigo)} -> {moeda(novo_preco)}"
        )
        return f"OK: preço de {p.nome} agora é {moeda(novo_preco)}."

    # ---------- Consultas e cálculos ----------
    def get_vendas(self, posicao_produto, dia):
        if not (0 <= posicao_produto < len(self._produtos)) or not self._dia_valido(dia):
            return 0
        return self._vendas[posicao_produto][dia - 1]

    def total_vendido_do_produto(self, posicao_produto):
        """Soma de uma LINHA da matriz."""
        if not (0 <= posicao_produto < len(self._produtos)):
            return 0
        soma = 0
        for d in range(7):
            soma += self._vendas[posicao_produto][d]
        return soma

    def total_vendido_no_dia(self, dia):
        """Soma de uma COLUNA da matriz."""
        if not self._dia_valido(dia):
            return 0
        soma = 0
        for i in range(len(self._produtos)):  # só as linhas em uso, não 20
            soma += self._vendas[i][dia - 1]
        return soma

    def get_faturamento_do_dia(self, dia):
        return self._faturamento_por_dia[dia - 1] if self._dia_valido(dia) else 0.0

    def get_faturamento_total(self):
        return sum(self._faturamento_por_dia)

    def produto_mais_vendido(self):
        melhor, melhor_total = None, 0
        for i, p in enumerate(self._produtos):
            total = self.total_vendido_do_produto(i)
            if total > melhor_total:
                melhor, melhor_total = p, total
        return melhor

    def dia_de_maior_faturamento(self):
        dia, maior = 0, 0.0
        for d in range(1, 8):
            if self._faturamento_por_dia[d - 1] > maior:
                dia, maior = d, self._faturamento_por_dia[d - 1]
        return dia

    def produtos_com_estoque_baixo(self):
        return [p for p in self._produtos if p.estoque_baixo(Padaria.LIMITE_ESTOQUE_BAIXO)]

    def valor_total_em_estoque(self):
        return sum(p.valor_em_estoque() for p in self._produtos)

    def get_historico(self):
        """Devolve uma CÓPIA do histórico."""
        return list(self._historico)

    # ---------- Auxiliares "privados" ----------
    def _indice_do_produto(self, codigo):
        for i, p in enumerate(self._produtos):
            if p.codigo == codigo:
                return i
        return -1

    def _existe_produto_com_nome(self, nome):
        return any(p.nome.lower() == nome.lower() for p in self._produtos)

    def _dia_valido(self, dia):
        return 1 <= dia <= 7

    def _registrar_no_historico(self, descricao):
        self._historico.append(f"{len(self._historico) + 1:03d} | {descricao}")
