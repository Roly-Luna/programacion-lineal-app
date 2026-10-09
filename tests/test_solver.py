import unittest
from backend.app.models import LPRequest
from backend.app.solver import solve_lp
from frontend.plotting import plot_model


def problem(a=80, b=50, mode='max', rows=None, non_negative=True):
    if rows is None:
        rows = [(2, 1, '<=', 40), (1, 2, '<=', 50)]
    return LPRequest(objective=dict(a=a, b=b, mode=mode),
        constraints=[dict(a=x, b=y, operator=op, c=c) for x, y, op, c in rows],
        non_negative=non_negative)


class SolverTests(unittest.TestCase):
    def test_maximum(self):
        p = problem()
        r = solve_lp(p)
        self.assertEqual(r.status, 'optimal')
        self.assertEqual((r.optimal_point.x, r.optimal_point.y), (10, 20))
        self.assertEqual(r.optimal_value, 1800)
        self.assertTrue(r.validated)
        self.assertEqual(len(r.vertices), 4)
        self.assertFalse(r.multiple_optima)
        self.assertTrue(len(plot_model(p, r, 1800, 60).data) >= 5)

    def test_minimum_unbounded_region(self):
        r = solve_lp(problem(40, 60, 'min', [(2, 1, '>=', 20), (1, 2, '>=', 25)]))
        self.assertEqual(r.optimal_value, 800)
        self.assertEqual((r.optimal_point.x, r.optimal_point.y), (5, 10))
        self.assertTrue(r.validated)

    def test_multiple(self):
        p = problem(1, 1, rows=[(1, 1, '<=', 10)])
        r = solve_lp(p)
        self.assertTrue(r.multiple_optima)
        self.assertFalse(r.optimal_face_unbounded)
        self.assertEqual(r.optimal_value, 10)
        fig = plot_model(p, r, 10, 12)
        gold = next(t for t in fig.data if t.name == 'Conjunto optimo visible')
        self.assertTrue(all(abs(x+y-10) < 1e-6 for x, y in zip(gold.x, gold.y)))

    def test_infeasible(self):
        self.assertEqual(solve_lp(problem(rows=[(1, 0, '<=', 1), (1, 0, '>=', 2)])).status, 'infeasible')

    def test_unbounded(self):
        self.assertEqual(solve_lp(problem(rows=[])).status, 'unbounded')

    def test_equality(self):
        r = solve_lp(problem(2, 1, rows=[(1, 1, '=', 10)]))
        self.assertEqual(r.optimal_value, 20)
        self.assertEqual(r.optimal_point.x, 10)

    def test_free_variables(self):
        r = solve_lp(problem(1, 1, rows=[(1, 0, '>=', -4), (1, 0, '<=', -1),
            (0, 1, '>=', -3), (0, 1, '<=', -2)], non_negative=False))
        self.assertEqual(r.optimal_value, -3)

    def test_no_vertices(self):
        r = solve_lp(problem(1, 0, 'min', [(1, 0, '>=', 2)], non_negative=False))
        self.assertEqual(r.status, 'optimal')
        self.assertEqual(r.optimal_value, 2)
        self.assertEqual(len(r.vertices), 0)
        self.assertTrue(r.multiple_optima)
        self.assertTrue(r.optimal_face_unbounded)

    def test_constant_objective(self):
        r = solve_lp(problem(0, 0, rows=[]))
        self.assertEqual(r.optimal_value, 0)
        self.assertTrue(r.multiple_optima)

    def test_single_point(self):
        r = solve_lp(problem(0, 0, rows=[(1, 0, '=', 2), (0, 1, '=', 3)]))
        self.assertFalse(r.multiple_optima)
        self.assertEqual(len(r.vertices), 1)

    def test_zero_constraint(self):
        self.assertEqual(solve_lp(problem(rows=[(0, 0, '<=', -1)])).status, 'infeasible')

    def test_parallel_redundant(self):
        r = solve_lp(problem(1, 1, rows=[(1, 1, '<=', 10), (2, 2, '<=', 20)]))
        self.assertEqual(r.optimal_value, 10)
        self.assertEqual(len(r.vertices), 3)


if __name__ == '__main__':
    unittest.main()
