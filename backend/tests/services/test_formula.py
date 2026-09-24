import unittest

from app.services.formula import evaluate_formula


class FormulaTests(unittest.TestCase):
    def test_scoring_arithmetic(self):
        for expression, variables, expected in [
            ("BOP / 5000000", {"BOP": 10000000}, 2),
            ("(2 * DPD) / 5000000", {"DPD": 5000000}, 2),
            ("(4 * DPkMD) / 5000000", {"DPkMD": 2500000}, 2),
            ("1 + (6 * PPDMhs)", {"PPDMhs": 0}, 1),
            ("8 - (8 * PJP)", {"PJP": 0.75}, 2),
            ("min(4, max(0, -x + 5))", {"x": 2}, 3),
            ("math.sqrt(x) + 2 ** 3", {"x": 4}, 10),
        ]:
            with self.subTest(expression=expression):
                self.assertEqual(evaluate_formula(expression, variables), expected)

    def test_piecewise_boundaries(self):
        for value in (0.2, 0.3, 0.5):
            self.assertTrue(evaluate_formula("0.2 <= PJP <= 0.5", {"PJP": value}))
        for value in (0.1, 0.6):
            self.assertFalse(evaluate_formula("0.2 <= PJP <= 0.5", {"PJP": value}))
        self.assertTrue(evaluate_formula("PJP < 0.2 or PJP > 0.5", {"PJP": 0.1}))

    def test_rejects_code_and_non_numeric_values(self):
        for expression in (
            "__import__('os').system('id')",
            "().__class__.__bases__",
            "math.__dict__",
            "[x for x in (1, 2)]",
            "(lambda: 1)()",
            "x[0]",
            "'text'",
            "True",
            "math.factorial(100000)",
            "max(x=1)",
            "1e309",
            "10 ** 1000000",
            "1 / 0",
            "x + 1",
            "1+" * 600,
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(
                    (ValueError, KeyError, SyntaxError, ArithmeticError)
                ):
                    evaluate_formula(expression, {})
        with self.assertRaises(ValueError):
            evaluate_formula("x", {"x": object()})


if __name__ == "__main__":
    unittest.main()
