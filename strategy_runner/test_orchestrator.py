import unittest

import orchestrator


class StrategyRunnerTests(unittest.TestCase):
    def test_discovers_expected_strategy_set(self):
        specs = orchestrator.discover_strategies()
        self.assertEqual(68, len(specs))
        self.assertIn("Bandtastic", {spec.name for spec in specs})
        self.assertTrue(any(spec.mode == "futures" for spec in specs))
        self.assertTrue(any(spec.lookahead_flag for spec in specs))

    def test_scoring_disqualifies_low_trade_and_lookahead_rows(self):
        base = {
            "mode": "spot", "timerange": "20240101-20250101", "status": "success",
            "total_trades": 100, "profit_total": 0.1, "sharpe": 1.0, "sortino": 1.1,
            "calmar": 0.8, "max_drawdown_account": 0.2, "lookahead_flag": False,
        }
        rows = [
            {**base, "name": "Good"},
            {**base, "name": "FewTrades", "total_trades": 2},
            {**base, "name": "Biased", "lookahead_flag": True},
        ]
        result = {row["name"]: row for row in orchestrator.score_rows(rows, orchestrator.load_settings())}
        self.assertTrue(result["Good"]["eligible"])
        self.assertFalse(result["FewTrades"]["eligible"])
        self.assertFalse(result["Biased"]["eligible"])


if __name__ == "__main__":
    unittest.main()
