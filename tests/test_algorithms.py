"""Автоматические тесты: запуск `python -m unittest discover -v` из корня проекта."""
import unittest

from tests.cases import A1_CASES, A2_CASES, A3_CASES, A4_CASES, E2E_CASES


def _make(cases):
    def test(self):
        for c in cases:
            with self.subTest(case=c.id, desc=c.desc):
                self.assertEqual(c.run(), c.expected)
    return test


class TestAlgorithms(unittest.TestCase):
    test_a1_slot_check = _make(A1_CASES)
    test_a2_session_time = _make(A2_CASES)
    test_a3_equipment = _make(A3_CASES)
    test_a4_bookings = _make(A4_CASES)
    test_end_to_end = _make(E2E_CASES)


if __name__ == "__main__":
    unittest.main()
