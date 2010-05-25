import unittest
import ast
from translate import State

def translate(s):
    a = ast.parse(s)
    #print(ast.dump(a))
    a.translate(State("sma.test"))

class TestTranslate(unittest.TestCase):
    def test_3plus4(self):
        translate("""print(3+4)""")
    
    def test_android_example(self):
        translate("""\
from android.app import Activity
from android.os import Bundle
from android.widget import TextView

class Start(Activity):
    def onCreate(state: Bundle):
        super().onCreate(state)
        tv = TextView(self)
        tv.setText("Hallo, Welt")
        self.setContentView(tv)""")

if __name__ == '__main__':
    unittest.main()
