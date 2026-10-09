from pathlib import Path
import unittest
from streamlit.testing.v1 import AppTest
from backend.app.models import LPRequest
from backend.app.solver import solve_lp
from frontend.plotting import plot_model, add_level_animation


class FrontendTests(unittest.TestCase):
    def test_interface(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'frontend/streamlit_app.py'),default_timeout=20).run()
        self.assertFalse(at.exception)
        def calculate():
            next(b for b in at.button if b.label=='Calcular resultado').click().run()
            self.assertFalse(at.exception)
        calculate()
        self.assertEqual(at.session_state['result']['optimal_value'],1800)
        at.slider[0].set_value(1000.).run()
        self.assertFalse(at.exception)
        for name,value in [('Compra de materia prima',800),('Varias decisiones con el mismo resultado',10)]:
            at.selectbox(key='example').select(name).run()
            calculate()
            self.assertEqual(at.session_state['result']['optimal_value'],value)
        self.assertTrue(at.session_state['result']['multiple_optima'])
        at.number_input(key='a').set_value(2.).run()
        self.assertTrue(at.info)

    def test_animation_ends_at_optimum(self):
        for a,b,mode,op,c,d in [(80,50,'max','<=',40,50),(40,60,'min','>=',20,25)]:
            p=LPRequest(objective=dict(a=a,b=b,mode=mode),constraints=[dict(a=2,b=1,operator=op,c=c),dict(a=1,b=2,operator=op,c=d)])
            r=solve_lp(p)
            fig=add_level_animation(plot_model(p,r,r.optimal_value,40),p,r,40)
            self.assertGreater(len(fig.frames),20)
            for x,y in zip(fig.frames[-1].data[0].x,fig.frames[-1].data[0].y):
                self.assertAlmostEqual(a*x+b*y,r.optimal_value,places=5)
