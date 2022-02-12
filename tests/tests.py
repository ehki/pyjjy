import unittest
import datetime

import pyjjy


class TestPyJJY(unittest.TestCase):
    def test_seq_case1(self):
        testtime = datetime.datetime(2022, 2, 12, 23, 46, 35, 792011)
        jj = pyjjy.JJYsignal()
        jj.update_seq(testtime)
        self.assertEqual(
            jj.dat,
            [-1,  # marker
             1, 0, 0,  # 10 minutes BCD
             0,
             0, 1, 1, 0,  # 1 minutes BCD
             -1, 0, 0,
             1, 0,  # 10 hours BCD
             0,
             0, 0, 1, 1,  # 1 hours BCD
             -1, 0, 0,
             0, 0,  # 100 days BCD
             0,
             0, 1, 0, 0,  # 10 days BCD
             -1,
             0, 0, 1, 1,  # 1 days BCD
             0, 0,
             1, 1,  # Parities
             0, -1, 0,
             0, 0, 1, 0,  # 10 years BCD
             0, 0, 1, 0,  # 1 years BCD
             -1,
             1, 1, 0,  # weekdays BCD
             0, 0, 0, 0, 0, 0, -1
             ]
        )

    def test_seq_case2(self):
        testtime = datetime.datetime(2024, 1, 12, 23, 34, 45, 123456)
        jj = pyjjy.JJYsignal()
        jj.update_seq(testtime)
        self.assertEqual(
            jj.dat,
            [-1,  # marker
             0, 1, 1,  # 10 minutes BCD
             0,
             0, 1, 0, 0,  # 1 minutes BCD
             -1, 0, 0,
             1, 0,  # 10 hours BCD
             0,
             0, 0, 1, 1,  # 1 hours BCD
             -1, 0, 0,
             0, 0,  # 100 days BCD
             0,
             0, 0, 0, 1,  # 10 days BCD
             -1,
             0, 0, 1, 0,  # 1 days BCD
             0, 0,
             1, 1,  # Parities
             0, -1, 0,
             0, 0, 1, 0,  # 10 years BCD
             0, 1, 0, 0,  # 1 years BCD
             -1,
             1, 0, 1,  # weekdays BCD
             0, 0, 0, 0, 0, 0, -1
             ]
        )
