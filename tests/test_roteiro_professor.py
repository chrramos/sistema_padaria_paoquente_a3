"""Roteiro de testes do enunciado (Quadro 17), na ordem T01 a T15.

Cobre o que dá para verificar sem o relatorio.py (T01, T13, T14 e T15 são
conferidos pelos NÚMEROS da Padaria, não pelo texto impresso do Relatorio).
Se o relatorio.py ainda não existir, um substituto vazio é usado só para
conseguir importar a Aplicacao.

Uso, na pasta do projeto:
    python -m unittest discover -s tests -v
"""
import contextlib
import io
import os
import sys
import types
import unittest
from unittest import mock

RAIZ = os.environ.get("PROJETO", os.getcwd())
sys.path.insert(0, RAIZ)

try:
    import padaria.relatorio  # noqa: F401
except ModuleNotFoundError:
    _stub = types.ModuleType("padaria.relatorio")

    class Relatorio:  # substituto: não imprime nada
        pass

    for _nome in ("imprimirEstoque", "imprimirVendasDaSemana", "imprimirEstoqueBaixo",
                  "imprimirFechamento", "imprimirHistorico", "imprimirResultadoBusca"):
        setattr(Relatorio, _nome, staticmethod(lambda *a, **k: None))
    _stub.Relatorio = Relatorio
    sys.modules["padaria.relatorio"] = _stub

from aplicacao import Aplicacao  # noqa: E402
from padaria.padaria import Padaria  # noqa: E402
from padaria.produto import Produto  # noqa: E402


def zerar_contador_de_codigos():
    """O contador de códigos é static e não volta a 1 sozinho. No programa real
    só existe uma Padaria; nos testes, zeramos para cada teste começar do código 1."""
    Produto._Produto__proximoCodigo = 1


def executar_com_teclado(funcao, respostas, *args):
    """Roda uma função da Aplicacao digitando `respostas`; devolve o que foi impresso."""
    saida = io.StringIO()
    with mock.patch("builtins.input", side_effect=respostas), contextlib.redirect_stdout(saida):
        funcao(*args)
    return saida.getvalue()


class TestDadosIniciais(unittest.TestCase):
    def setUp(self):
        zerar_contador_de_codigos()
        self.p = Padaria("Padaria Pão Quente")
        Aplicacao._Aplicacao__carregarDadosIniciais(self.p)

    def test_produtos_e_codigos_do_quadro_11(self):
        self.assertEqual([x.codigo for x in self.p.get_produtos()], [1, 2, 3, 4, 5])
        self.assertEqual(self.p.get_produtos()[0].nome, "Pão francês")

    def test_matriz_do_quadro_9(self):
        esperado = [[120, 60, 0], [15, 0, 20], [0, 2, 0], [0, 0, 10], [30, 0, 25]]
        for linha, valores in enumerate(esperado):
            for dia, qtd in enumerate(valores, start=1):
                self.assertEqual(self.p.get_vendas(linha, dia), qtd, f"linha {linha} dia {dia}")
        self.assertEqual([self.p.total_vendido_do_produto(i) for i in range(5)],
                         [180, 35, 2, 10, 55])
        self.assertEqual([self.p.total_vendido_no_dia(d) for d in (1, 2, 3, 4)], [165, 62, 55, 0])

    def test_valores_do_enunciado(self):
        self.assertAlmostEqual(self.p.valor_total_em_estoque(), 454.50)
        self.assertAlmostEqual(self.p.get_faturamento_total(), 683.50)
        self.assertEqual([x.nome for x in self.p.produtos_com_estoque_baixo()], ["Bolo de cenoura"])
        self.assertEqual(len(self.p.get_historico()), 13)
        self.assertTrue(self.p.get_historico()[5].startswith("006 | Venda: 120 x Pão francês (Seg) = R$ 90,00"))


class TestRoteiroQuadro17(unittest.TestCase):
    """T01 a T15, em sequência, no mesmo estado (como o professor pede)."""

    def test_roteiro_completo(self):
        zerar_contador_de_codigos()
        p = Padaria("Padaria Pão Quente")
        Aplicacao._Aplicacao__carregarDadosIniciais(p)

        # T01: 5 produtos; valor em estoque R$ 454,50
        self.assertEqual(p.get_quantidade_de_produtos(), 5)
        self.assertAlmostEqual(p.valor_total_em_estoque(), 454.50)

        # T02: preço "abc" pede de novo; depois "3,50", quantidade 40
        saida = executar_com_teclado(Aplicacao._Aplicacao__cadastrarProduto,
                                     ["Broa de milho", "Pães", "abc", "3,50", "40"], p)
        self.assertIn("Valor inválido", saida)
        self.assertIn("OK: produto cadastrado com o código 6.", saida)

        # T03: nome duplicado (ignora maiúsculas)
        self.assertTrue(p.cadastrar_produto("pão francês", "Pães", 1, 10)
                        .startswith("ERRO: já existe um produto chamado"))
        # T04: preço 0
        self.assertEqual(p.cadastrar_produto("Rosca", "Pães", 0, 10),
                         "ERRO: o preço deve ser maior que zero.")
        # T05: estoque insuficiente
        self.assertEqual(p.registrar_venda(3, 5, 4),
                         "ERRO: estoque insuficiente. Disponível: 4 unidade(s).")
        # T06: venda aceita
        self.assertEqual(p.registrar_venda(1, 10, 4),
                         "OK: venda registrada. Total: R$ 7,50. Estoque restante: 10.")
        # T07: dia inválido
        self.assertTrue(p.registrar_venda(2, 1, 8).startswith("ERRO: dia inválido"))
        # T08: código inexistente
        self.assertEqual(p.registrar_venda(99, 1, 1), "ERRO: produto de código 99 não encontrado.")

        # T09: opção 99 e letra x no menu; depois 0 para sair
        saida = executar_com_teclado(Aplicacao.main, ["99", "x", "0"])
        self.assertIn("Opção inválida. Digite um número de 0 a 10.", saida)
        self.assertIn("Valor inválido: digite um número inteiro.", saida)
        self.assertIn("Encerrando o sistema", saida)

        # T10: repor 12 no Bolo
        self.assertEqual(p.repor_estoque(3, 12), "OK: estoque de Bolo de cenoura agora é 16.")
        # T11: preço negativo
        self.assertEqual(p.alterar_preco(1, -2), "ERRO: o preço deve ser maior que zero.")
        # T12: busca "pão" -> 2 produtos
        self.assertEqual(len(p.buscar_por_nome("pão")), 2)
        # T13: nenhum estoque baixo
        self.assertEqual(p.produtos_com_estoque_baixo(), [])
        # T14: coluna Qui com total 10; total geral 292
        self.assertEqual(p.total_vendido_no_dia(4), 10)
        self.assertEqual(sum(p.total_vendido_no_dia(d) for d in range(1, 8)), 292)
        # T15: fechamento R$ 691,00 e estoque R$ 923,00
        self.assertAlmostEqual(p.get_faturamento_total(), 691.00)
        self.assertAlmostEqual(p.valor_total_em_estoque(), 923.00)


if __name__ == "__main__":
    unittest.main(verbosity=2)
