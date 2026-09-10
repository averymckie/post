# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

import fwcheck.diagnostics
import unittest
from hypothesis import given, strategies as st


class TestEquivalentZ3_Integer_IntervalCvc5_Integer_Interval(unittest.TestCase):

    @given(
        coefficient=st.integers(),
        lower=st.integers(),
        target=st.integers(),
        upper=st.integers(),
    )
    def test_equivalent_z3_integer_interval_cvc5_integer_interval(
        self, coefficient: int, lower: int, target: int, upper: int
    ) -> None:
        result_z3_integer_interval = fwcheck.diagnostics.z3_integer_interval(
            lower=lower, upper=upper, coefficient=coefficient, target=target
        )
        result_cvc5_integer_interval = fwcheck.diagnostics.cvc5_integer_interval(
            lower=lower, upper=upper, coefficient=coefficient, target=target
        )
        self.assertEqual(result_z3_integer_interval, result_cvc5_integer_interval)
