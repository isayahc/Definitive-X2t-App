from app.Frequency import Frequency, MultiDay, IntraDay, Daily, Weekly, Monthly
import pandas as pd
from datetime import date
import unittest
import pytest

@pytest.fixture
def IntraDay():
    return IntraDay('spy',1)


def test_Frequency_Constructor():
    f = Frequency('spy')

def test_Frequency_Constructor():
    f = Frequency('spy')
    assert f.end is date
    assert f.start is date


def test_Daily_Constructor():
    d = Daily('spy')
    assert d.collectData() is pd.DataFrame

def test_Weekly_Constructor():
    w = Weekly('spy')
    assert w.collectData() is pd.DataFrame

def test_Intra_Constructor():
    i = IntraDay('spy',1)
    assert i.collectData() is pd.DataFrame

# def test_MultiDay_Constructor():
#     m = MultiDay('spy')
#     assert m.collectData() is pd.DataFrame
class TestExample(unittest.TestCase):

    def Testx(self):
        results = Daily('spy')
        self.assertIsInstance(results, pd.DataFrame)