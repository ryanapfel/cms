import unittest
from ..overview import *
import pandas as pd
import numpy as np
import os


class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        df = pd.DataFrame([1, 2, 3], columns=["a"])
        self.assertEqual(df["a"].iloc[0], 1)
