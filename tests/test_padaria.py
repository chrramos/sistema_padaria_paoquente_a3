"""Testes da Padaria Pão Quente.

Uso (a partir da pasta do projeto, onde fica aplicacao.py e a pasta padaria/):
    python -m unittest tests/test_padaria.py -v
ou, de qualquer lugar:
    PROJETO=/caminho/do/projeto python -m unittest test_padaria -v
"""
import ast
import os
import sys
import unittest

RAIZ = os.environ.get("PROJETO", os.getcwd())
sys.path.insert(0, RAIZ)

from padaria.padaria import Padaria  # noqa: E402


def cod(padaria, nome):
    """Código de um produto pelo nome (não presume que os códigos começam em 1)."""
    return padaria.buscar_por_nome(nome)[0].codigo


def nova_padaria():
    """Padaria com 3 produtos de valores fáceis de conferir."""
    p = Padaria("Teste")
    p.cadastrar_produto("Pão", "Pães", 1.00, 100)
    p.cadastrar_produto("Bolo", "Doces", 20.00, 10)
    p.cadastrar_produto("Café", "Bebidas", 5.00, 4)
    return p


class TestIntegracao(unittest.TestCase):
    def test_aplicacao_chama_apenas_metodos_que_existem_na_padaria(self):
        """Todo `padaria.xxx(...)` usado em aplicacao.py existe na classe Padaria?"""
        with open(os.path.join(RAIZ, "aplicacao.py"), encoding="utf-8") as f:
            arvore = ast.parse(f.read())
        usados = {
            n.func.attr for n in ast.walk(arvore)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "padaria"
        }
        faltando = sorted(m for m in usados if not hasattr(Padaria, m))
        self.assertEqual(faltando, [], f"Aplicacao chama métodos inexistentes: {faltando}")


class TestCadastro(unittest.TestCase):
    def test_cadastro_valido(self):
        p = Padaria("T")
        msg = p.cadastrar_produto("Pão", "Pães", 0.75, 10)
        self.assertTrue(msg.startswith("OK"), msg)
        self.assertEqual(p.get_quantidade_de_produtos(), 1)

    def test_nome_duplicado_e_recusado(self):
        p = Padaria("T")
        p.cadastrar_produto("Pão", "Pães", 0.75, 10)
        msg = p.cadastrar_produto("Pão", "Pães", 1.00, 5)
        self.assertTrue(msg.startswith("ERRO"), msg)
        self.assertEqual(p.get_quantidade_de_produtos(), 1)

    def test_nome_duplicado_ignora_maiusculas_e_espacos(self):
        p = Padaria("T")
        p.cadastrar_produto("Pão", "Pães", 0.75, 10)
        msg = p.cadastrar_produto("  pÃo ", "Pães", 1.00, 5)
        self.assertTrue(msg.startswith("ERRO"), msg)

    def test_nome_vazio(self):
        p = Padaria("T")
        self.assertTrue(p.cadastrar_produto("   ", "x", 1.0, 1).startswith("ERRO"))

    def test_preco_zero_ou_negativo(self):
        p = Padaria("T")
        self.assertTrue(p.cadastrar_produto("A", "x", 0, 1).startswith("ERRO"))
        self.assertTrue(p.cadastrar_produto("B", "x", -2.5, 1).startswith("ERRO"))
        self.assertEqual(p.get_quantidade_de_produtos(), 0)

    def test_quantidade_inicial_negativa(self):
        p = Padaria("T")
        self.assertTrue(p.cadastrar_produto("A", "x", 1.0, -1).startswith("ERRO"))
        self.assertEqual(p.get_quantidade_de_produtos(), 0)

    def test_categoria_vazia_vira_sem_categoria(self):
        p = Padaria("T")
        p.cadastrar_produto("A", "", 1.0, 1)
        self.assertEqual(p.get_produtos()[0].categoria, "Sem categoria")

    def test_limite_de_20_produtos(self):
        p = Padaria("T")
        for i in range(Padaria.MAX_PRODUTOS):
            self.assertTrue(p.cadastrar_produto(f"Item{i}", "x", 1.0, 1).startswith("OK"))
        self.assertTrue(p.cadastrar_produto("Item21", "x", 1.0, 1).startswith("ERRO"))
        self.assertEqual(p.get_quantidade_de_produtos(), 20)

    def test_get_produtos_devolve_copia(self):
        p = nova_padaria()
        p.get_produtos().clear()
        self.assertEqual(p.get_quantidade_de_produtos(), 3)


class TestVendas(unittest.TestCase):
    def test_venda_reduz_estoque_e_calcula_total(self):
        p = nova_padaria()
        c = cod(p, "Pão")
        msg = p.registrar_venda(c, 30, 1)
        self.assertTrue(msg.startswith("OK"), msg)
        self.assertEqual(p.buscar_por_codigo(c).quantidade, 70)
        self.assertAlmostEqual(p.get_faturamento_do_dia(1), 30.00)

    def test_venda_do_estoque_inteiro(self):
        p = nova_padaria()
        c = cod(p, "Café")
        self.assertTrue(p.registrar_venda(c, 4, 2).startswith("OK"))
        self.assertEqual(p.buscar_por_codigo(c).quantidade, 0)

    def test_estoque_insuficiente_nao_altera_nada(self):
        p = nova_padaria()
        c = cod(p, "Café")
        msg = p.registrar_venda(c, 5, 1)  # só há 4
        self.assertTrue(msg.startswith("ERRO"), msg)
        self.assertEqual(p.buscar_por_codigo(c).quantidade, 4)
        self.assertEqual(p.get_faturamento_total(), 0.0)
        self.assertEqual(p.total_vendido_no_dia(1), 0)
        self.assertEqual(len(p.get_historico()), 3)  # só os 3 cadastros

    def test_entradas_invalidas_na_venda(self):
        p = nova_padaria()
        c = cod(p, "Pão")
        self.assertTrue(p.registrar_venda(9999, 1, 1).startswith("ERRO"))  # código
        self.assertTrue(p.registrar_venda(c, 0, 1).startswith("ERRO"))     # unidades 0
        self.assertTrue(p.registrar_venda(c, -3, 1).startswith("ERRO"))    # negativa
        self.assertTrue(p.registrar_venda(c, 1, 0).startswith("ERRO"))     # dia 0
        self.assertTrue(p.registrar_venda(c, 1, 8).startswith("ERRO"))     # dia 8
        self.assertEqual(p.buscar_por_codigo(c).quantidade, 100)
        self.assertEqual(p.get_faturamento_total(), 0.0)

    def test_matriz_de_vendas_por_produto_e_dia(self):
        p = nova_padaria()
        pao, bolo = cod(p, "Pão"), cod(p, "Bolo")
        p.registrar_venda(pao, 10, 1)
        p.registrar_venda(pao, 5, 1)
        p.registrar_venda(bolo, 2, 1)
        p.registrar_venda(pao, 7, 3)
        self.assertEqual(p.get_vendas(0, 1), 15)
        self.assertEqual(p.get_vendas(1, 1), 2)
        self.assertEqual(p.get_vendas(0, 3), 7)
        self.assertEqual(p.total_vendido_do_produto(0), 22)
        self.assertEqual(p.total_vendido_no_dia(1), 17)
        self.assertEqual(p.produto_mais_vendido().nome, "Pão")


class TestReposicaoEPreco(unittest.TestCase):
    def test_reposicao_soma_ao_estoque(self):
        p = nova_padaria()
        c = cod(p, "Café")
        self.assertTrue(p.repor_estoque(c, 6).startswith("OK"))
        self.assertEqual(p.buscar_por_codigo(c).quantidade, 10)

    def test_reposicao_invalida(self):
        p = nova_padaria()
        c = cod(p, "Café")
        self.assertTrue(p.repor_estoque(c, 0).startswith("ERRO"))
        self.assertTrue(p.repor_estoque(c, -2).startswith("ERRO"))
        self.assertTrue(p.repor_estoque(9999, 5).startswith("ERRO"))
        self.assertEqual(p.buscar_por_codigo(c).quantidade, 4)

    def test_alterar_preco(self):
        p = nova_padaria()
        c = cod(p, "Bolo")
        self.assertTrue(p.alterar_preco(c, 25.50).startswith("OK"))
        self.assertAlmostEqual(p.buscar_por_codigo(c).preco, 25.50)

    def test_preco_invalido_mantem_o_antigo(self):
        p = nova_padaria()
        c = cod(p, "Bolo")
        self.assertTrue(p.alterar_preco(c, 0).startswith("ERRO"))
        self.assertTrue(p.alterar_preco(c, -1).startswith("ERRO"))
        self.assertTrue(p.alterar_preco(9999, 5).startswith("ERRO"))
        self.assertAlmostEqual(p.buscar_por_codigo(c).preco, 20.00)

    def test_novo_preco_nao_muda_faturamento_ja_registrado(self):
        p = nova_padaria()
        c = cod(p, "Bolo")
        p.registrar_venda(c, 2, 1)           # 2 x 20,00 = 40,00
        p.alterar_preco(c, 30.00)
        self.assertAlmostEqual(p.get_faturamento_do_dia(1), 40.00)
        p.registrar_venda(c, 1, 2)           # 1 x 30,00
        self.assertAlmostEqual(p.get_faturamento_do_dia(2), 30.00)


class TestFaturamento(unittest.TestCase):
    def test_faturamento_por_dia_e_semanal(self):
        p = nova_padaria()
        pao, bolo, cafe = cod(p, "Pão"), cod(p, "Bolo"), cod(p, "Café")
        p.registrar_venda(pao, 10, 1)    # 10,00 (Seg)
        p.registrar_venda(bolo, 2, 1)    # 40,00 (Seg)
        p.registrar_venda(cafe, 3, 3)    # 15,00 (Qua)
        p.registrar_venda(bolo, 1, 7)    # 20,00 (Dom)
        self.assertAlmostEqual(p.get_faturamento_do_dia(1), 50.00)
        self.assertAlmostEqual(p.get_faturamento_do_dia(2), 0.00)
        self.assertAlmostEqual(p.get_faturamento_do_dia(3), 15.00)
        self.assertAlmostEqual(p.get_faturamento_do_dia(7), 20.00)
        self.assertAlmostEqual(p.get_faturamento_total(), 85.00)
        self.assertEqual(p.dia_de_maior_faturamento(), 1)

    def test_dia_invalido_devolve_zero(self):
        p = nova_padaria()
        self.assertEqual(p.get_faturamento_do_dia(0), 0.0)
        self.assertEqual(p.get_faturamento_do_dia(8), 0.0)

    def test_sem_vendas(self):
        p = nova_padaria()
        self.assertEqual(p.get_faturamento_total(), 0.0)
        self.assertEqual(p.dia_de_maior_faturamento(), 0)
        self.assertIsNone(p.produto_mais_vendido())


class TestEstoqueBaixo(unittest.TestCase):
    def test_limite_e_menor_que_5(self):
        p = Padaria("T")
        p.cadastrar_produto("Quatro", "x", 1.0, 4)
        p.cadastrar_produto("Cinco", "x", 1.0, 5)
        p.cadastrar_produto("Zero", "x", 1.0, 0)
        p.cadastrar_produto("Muito", "x", 1.0, 50)
        nomes = sorted(x.nome for x in p.produtos_com_estoque_baixo())
        self.assertEqual(nomes, ["Quatro", "Zero"])

    def test_venda_faz_produto_entrar_na_lista_e_reposicao_tira(self):
        p = Padaria("T")
        p.cadastrar_produto("Bolo", "x", 10.0, 8)
        c = cod(p, "Bolo")
        self.assertEqual(p.produtos_com_estoque_baixo(), [])
        p.registrar_venda(c, 4, 1)   # sobram 4
        self.assertEqual([x.nome for x in p.produtos_com_estoque_baixo()], ["Bolo"])
        p.repor_estoque(c, 10)       # 14
        self.assertEqual(p.produtos_com_estoque_baixo(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
