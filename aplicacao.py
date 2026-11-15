import math
import sys

from padaria.padaria import Padaria
from padaria.relatorio import Relatorio


class Aplicacao:

    @staticmethod
    def main():
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

        padaria = Padaria("Padaria Pão Quente")
        Aplicacao.__carregarDadosIniciais(padaria)

        opcao = -1
        while opcao != 0:
            Aplicacao.__mostrarMenu()
            opcao = Aplicacao.__lerInteiro("Escolha uma opção: ")
            match opcao:
                case 1:
                    Aplicacao.__cadastrarProduto(padaria)
                case 2:
                    Relatorio.imprimirEstoque(padaria)
                case 3:
                    Aplicacao.__registrarVenda(padaria)
                case 4:
                    Aplicacao.__reporEstoque(padaria)
                case 5:
                    Aplicacao.__alterarPreco(padaria)
                case 6:
                    Aplicacao.__buscarProduto(padaria)
                case 7:
                    Relatorio.imprimirVendasDaSemana(padaria)
                case 8:
                    Relatorio.imprimirEstoqueBaixo(padaria)
                case 9:
                    Relatorio.imprimirFechamento(padaria)
                case 10:
                    Relatorio.imprimirHistorico(padaria)
                case 0:
                    Relatorio.imprimirFechamento(padaria)
                    print("Encerrando o sistema. Até logo!")
                case _:
                    print("Opção inválida. Digite um número de 0 a 10.")

    @staticmethod
    def __mostrarMenu():
        print()
        print("===== PADARIA PÃO QUENTE =====")
        print(" 1 - Cadastrar produto")
        print(" 2 - Listar estoque")
        print(" 3 - Registrar venda")
        print(" 4 - Repor estoque")
        print(" 5 - Alterar preço")
        print(" 6 - Buscar produto por nome")
        print(" 7 - Relatório de vendas da semana")
        print(" 8 - Produtos com estoque baixo")
        print(" 9 - Fechamento")
        print("10 - Histórico de operações")
        print(" 0 - Sair")

    @staticmethod
    def __cadastrarProduto(padaria):
        print("--- Cadastro de produto ---")
        nome = Aplicacao.__lerTexto("Nome: ")
        categoria = input("Categoria (Enter para 'Sem categoria'): ").strip()
        preco = Aplicacao.__lerDecimal("Preço (R$): ")
        quantidade = Aplicacao.__lerInteiro("Quantidade inicial: ")
        print(padaria.cadastrar_produto(nome, categoria, preco, quantidade))

    @staticmethod
    def __registrarVenda(padaria):
        print("--- Registro de venda ---")
        codigo = Aplicacao.__lerInteiro("Código do produto: ")
        unidades = Aplicacao.__lerInteiro("Quantidade vendida: ")
        dia = Aplicacao.__lerInteiro(
            "Dia (1-Seg 2-Ter 3-Qua 4-Qui 5-Sex 6-Sáb 7-Dom): ")
        print(padaria.registrar_venda(codigo, unidades, dia))

    @staticmethod
    def __reporEstoque(padaria):
        print("--- Reposição de estoque ---")
        codigo = Aplicacao.__lerInteiro("Código do produto: ")
        unidades = Aplicacao.__lerInteiro("Unidades a repor: ")
        print(padaria.repor_estoque(codigo, unidades))

    @staticmethod
    def __alterarPreco(padaria):
        print("--- Alteração de preço ---")
        codigo = Aplicacao.__lerInteiro("Código do produto: ")
        novoPreco = Aplicacao.__lerDecimal("Novo preço (R$): ")
        print(padaria.alterar_preco(codigo, novoPreco))

    @staticmethod
    def __buscarProduto(padaria):
        print("--- Busca por nome ---")
        trecho = Aplicacao.__lerTexto("Parte do nome: ")
        Relatorio.imprimirResultadoBusca(padaria.buscar_por_nome(trecho), trecho)

    @staticmethod
    def __carregarDadosIniciais(padaria):
        padaria.cadastrar_produto("Pão francês", "Pães", 0.75, 200)
        padaria.cadastrar_produto("Pão de queijo", "Salgados", 4.50, 60)
        padaria.cadastrar_produto("Bolo de cenoura", "Doces", 28.00, 6)
        padaria.cadastrar_produto("Sonho", "Doces", 6.00, 25)
        padaria.cadastrar_produto("Café coado", "Bebidas", 5.00, 80)

        vendas = [
            (1, 120, 1), (2, 15, 1), (5, 30, 1),
            (1, 60, 2), (3, 2, 2),
            (4, 10, 3), (2, 20, 3), (5, 25, 3),
        ]
        for codigo, unidades, dia in vendas:
            padaria.registrar_venda(codigo, unidades, dia)

    @staticmethod
    def __lerInteiro(mensagem):
        while True:
            texto = input(mensagem).strip()
            try:
                return int(texto)
            except ValueError:
                print("Valor inválido: digite um número inteiro.")

    @staticmethod
    def __lerDecimal(mensagem):
        while True:
            texto = input(mensagem).strip().replace(",", ".")
            try:
                valor = float(texto)
                if math.isfinite(valor):
                    return valor
            except ValueError:
                pass
            print("Valor inválido: digite um número, como 5,50.")

    @staticmethod
    def __lerTexto(mensagem):
        while True:
            texto = input(mensagem).strip()
            if texto:
                return texto
            print("Este campo não pode ficar vazio.")


if __name__ == "__main__":
    Aplicacao.main()
