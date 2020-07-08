import unittest 
from app.Tw import Tw, LocalTw, CloudTw

class Test_LocalTW(unittest.TestCase):
    def test_add_data(self):
        x = {'a': [1, 3, 4], 'b': [2]}
        result = LocalTw('spy',1).add_data({'a':7}, x)
        self.assertEqual(result,{'a': [1, 3, 4,7], 'b': [2]} )