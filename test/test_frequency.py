from app.Frequency import Frequency, MultiDay, IntraDay, Daily, Weekly, Monthly
import pandas as pd

def test_Frequency_Constructor():
    f = Frequency('spy')


def test_Daily_Constructor():
    d = Daily('spy')
    assert d.collectData() is pd.DataFrame

def test_Weekly_Constructor():
    w = Weekly('spy')
    assert w.collectData() is pd.DataFrame

# def test_MultiDay_Constructor():
#     m = MultiDay('spy')
#     assert m.collectData() is pd.DataFrame
