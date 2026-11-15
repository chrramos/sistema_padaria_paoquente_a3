from padaria.padaria import moeda

class Relatorio:

    #Estoque
    @staticmethod
    def imprimirEstoque(padaria):
        print("\n===== ESTOQUE DA PADARIA =====")

        produtos = padaria.get_produtos()
        total_estoque = 0

        for produto in produtos:
            valor_estoque = produto.preco * produto.quantidade
            total_estoque += valor_estoque

            print(f"Código: {produto.codigo} | Produto: {produto.nome} | Categoria: {produto.categoria} | Preço: {moeda(produto.preco)} | Quantidade: {produto.quantidade} | Valor em estoque: {moeda(valor_estoque)}")

        print(f"Valor total do estoque: {moeda(total_estoque)}")
        print(80*"=")

    #Vendas da semana
    @staticmethod
    def imprimirVendasDaSemana(padaria):
        print("\n===== VENDAS DA SEMANA =====")

        produtos = padaria.get_produtos()
        dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

        print(f"{'Produto':<20}", end="")

        for dia in dias:
            print(f"{dia:>6}", end="")

        print(f"{'Total':>8}")

        for i, produto in enumerate(produtos):
            print(f"{produto.nome:<20}", end="")

            for dia in range(1, 8):
                quantidade = padaria.get_vendas(i, dia)
                print(f"{quantidade:>6}", end="")

            total = padaria.total_vendido_do_produto(i)
            print(f"{total:>8}")

        print("-" * 70)
        print(f"{'TOTAL':<20}", end="")

        for dia in range(1, 8):
            total_dia = padaria.total_vendido_no_dia(dia)
            print(f"{total_dia:>6}", end="")

        total_semana = sum(
            padaria.total_vendido_no_dia(dia)
            for dia in range(1, 8)
        )

        print(f"{total_semana:>8}")

    #Verificação Estoquie Baixou
    @staticmethod
    def imprimirEstoqueBaixo(padaria):
        print("\n===== PRODUTOS COM ESTOQUE BAIXO =====")

        produtos = padaria.produtos_com_estoque_baixo()

        if not produtos:
            print("Nenhum produto com estoque baixo.")
        else:
            for produto in produtos:
                print(
                    f"Produto: {produto.nome} | "
                    f"Quantidade: {produto.quantidade}"
                )

    #Fecahmento semanal
    @staticmethod
    def imprimirFechamento(padaria):
        print("\n===== FECHAMENTO SEMANAL =====")

        for dia in range(1, 8):
            faturamento = padaria.get_faturamento_do_dia(dia)
            nome_dia = padaria.DIAS[dia - 1]

            print(f"{nome_dia}: {moeda(faturamento)}")

        total = padaria.get_faturamento_total()
        print(f"\nFaturamento total: {moeda(total)}")

        valor_estoque = padaria.valor_total_em_estoque()
        print(f"Valor total em estoque: {moeda(valor_estoque)}")

        produto = padaria.produto_mais_vendido()

        if produto is not None:
            print(f"Produto mais vendido: {produto.nome}")
        else:
            print("Nenhuma venda registrada.")

        dia = padaria.dia_de_maior_faturamento()

        if dia != 0:
            print(f"Dia de maior faturamento: {padaria.DIAS[dia - 1]}")
        else:
            print("Nenhum faturamento registrado.")

        quantidade_baixo = len(padaria.produtos_com_estoque_baixo())
        print(f"Produtos com estoque baixo: {quantidade_baixo}")

        quantidade_operacoes = len(padaria.get_historico())
        print(f"Operações registradas: {quantidade_operacoes}")

    #Historico de operações
    @staticmethod
    def imprimirHistorico(padaria):
        print("\n===== HISTÓRICO DE OPERAÇÕES =====")

        historico = padaria.get_historico()

        if not historico:
            print("Nenhuma operação registrada.")
        else:
            for operacao in historico:
                print(operacao)

    #Resultado Busca
    @staticmethod
    def imprimirResultadoBusca(produtos, trecho):
        print(f"\n===== BUSCA POR: {trecho} =====")

        if not produtos:
            print("Nenhum produto encontrado.")
        else:
            for produto in produtos:
                print(
                    f"Código: {produto.codigo} | "
                    f"Nome: {produto.nome} | "
                    f"Categoria: {produto.categoria} | "
                    f"Preço: {moeda(produto.preco)} | "
                    f"Quantidade: {produto.quantidade}"
                )