from pathlib import Path
import unittest

from src.analysis import clean_and_prepare, compute_kpis, group_churn, load_dataset


ROOT = Path(__file__).resolve().parents[1]


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = load_dataset(ROOT / "data" / "European_Bank.csv")
        cls.prepared, cls.metadata = clean_and_prepare(raw)

    def test_source_has_expected_population(self):
        self.assertEqual(len(self.prepared), 10_000)
        self.assertEqual(self.metadata["duplicate_rows_removed"], 0)
        self.assertEqual(self.metadata["rows_with_missing_core_fields_removed"], 0)

    def test_binary_fields_are_valid(self):
        for column in ["HasCrCard", "IsActiveMember", "Exited"]:
            self.assertTrue(set(self.prepared[column].unique()).issubset({0, 1}))

    def test_customer_segments_are_populated(self):
        for column in ["AgeGroup", "CreditScoreBand", "TenureGroup", "BalanceSegment", "ActivityStatus"]:
            self.assertFalse(self.prepared[column].isna().any(), column)

    def test_kpis_reconcile(self):
        kpis = compute_kpis(self.prepared)
        self.assertEqual(kpis["total_customers"], kpis["churned_customers"] + kpis["retained_customers"])
        self.assertAlmostEqual(kpis["overall_churn_rate"], 0.2037, places=6)
        self.assertEqual(kpis["high_value_churned_customers"], 367)

    def test_geography_table_reconciles(self):
        table = group_churn(self.prepared, "Geography")
        self.assertEqual(int(table["customers"].sum()), len(self.prepared))
        self.assertEqual(int(table["churned"].sum()), int(self.prepared["Exited"].sum()))
        self.assertEqual(set(table["Geography"]), {"France", "Spain", "Germany"})

    def test_high_value_threshold_is_recorded(self):
        threshold = self.metadata["thresholds"]["high_value_balance_threshold_75th_percentile"]
        self.assertIsNotNone(threshold)
        self.assertGreater(threshold, 0)
        self.assertEqual(int(self.prepared["HighValueFlag"].sum()), 1596)


if __name__ == "__main__":
    unittest.main()
