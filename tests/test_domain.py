import unittest, copy, json
from decimal import Decimal
from pathlib import Path
from cryptolab import analyze
from cryptolab.engine import *

EXAMPLE = json.loads(Path("examples/input.json").read_text())


class DomainTests(unittest.TestCase):
    def test_nonce_packing(self):
        self.assertEqual(
            [t["id"] for t in analyze(EXAMPLE)["blocks"][0]["transactions"]],
            ["b0", "a0", "a1"],
        )

    def test_base_update(self):
        self.assertEqual(next_base_fee(100, 100000, 100000), 112)
        self.assertEqual(next_base_fee(100, 0, 100000), 88)

    def test_minimum_increase(self):
        self.assertEqual(next_base_fee(1, 50001, 100000), 2)

    def test_fee_conservation(self):
        r = analyze(EXAMPLE)
        self.assertEqual(
            sum(t["cost"] for b in r["blocks"] for t in b["transactions"]),
            r["burned"] + r["validator_tips"],
        )

    def test_capped_transaction(self):
        d = copy.deepcopy(EXAMPLE)
        d["transactions"][0]["max_fee"] = 50
        r = analyze(d)
        self.assertEqual(len(r["pending"]), 2)
