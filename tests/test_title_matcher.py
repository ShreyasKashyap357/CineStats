"""Tests for title matcher."""
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.logic.title_matcher import normalize_title, match_titles, merge_movie_data


class TestNormalizeTitle(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(normalize_title("The Batman"), "the batman")

    def test_punctuation_removed(self):
        self.assertEqual(normalize_title("Spider-Man: No Way Home"), "spiderman no way home")

    def test_whitespace_collapsed(self):
        self.assertEqual(normalize_title("  The   Dark   Knight  "), "the dark knight")

    def test_unicode(self):
        result = normalize_title("Laapataa Ladies")
        self.assertEqual(result, "laapataa ladies")


class TestMatchTitles(unittest.TestCase):

    def setUp(self):
        self.candidates = [
            {"title_normalized": "the batman", "release_date": "2022-03-04"},
            {"title_normalized": "batman begins", "release_date": "2005-06-15"},
            {"title_normalized": "the dark knight", "release_date": "2008-07-18"},
            {"title_normalized": "pushpa 2 the rule", "release_date": "2024-12-05"},
        ]

    def test_exact_match(self):
        result = match_titles("The Batman", self.candidates, "2022-03-04")
        self.assertIsNotNone(result)
        self.assertEqual(result["match_confidence"], 1.0)
        self.assertEqual(result["match_method"], "exact")

    def test_fuzzy_match(self):
        result = match_titles("Pushpa 2: The Rule", self.candidates)
        self.assertIsNotNone(result)
        self.assertGreater(result["match_confidence"], 0.8)
        self.assertEqual(result["matched_title"], "pushpa 2 the rule")

    def test_no_match(self):
        result = match_titles("Completely Random Title XYZ", self.candidates)
        self.assertIsNone(result)

    def test_manual_override(self):
        overrides = {"inception 2010": "the dark knight"}
        result = match_titles("Inception 2010", self.candidates, overrides=overrides)
        self.assertIsNotNone(result)
        self.assertEqual(result["match_confidence"], 1.0)
        self.assertEqual(result["match_method"], "manual_override")


class TestMergeMovieData(unittest.TestCase):

    def test_merge_all_sources(self):
        bom = {
            "title_normalized": "pushpa 2", "title_display": "Pushpa 2",
            "worldwide_gross_usd": 200_000_000, "domestic_gross_usd": 50_000_000,
            "foreign_gross_usd": 150_000_000, "opening_weekend_usd": 30_000_000,
            "release_date": "2024-12-05",
        }
        sacnilk = {
            "india_net_cr": 1050.0, "india_gross_cr": 1250.0, "verdict": "All-Time Blockbuster",
            "language": "Telugu",
        }
        tmdb = {
            "genre": "Action, Thriller", "runtime": 175, "origin_country": "IN",
            "tmdb_id": 12345,
        }

        merged = merge_movie_data(bom, sacnilk, tmdb, match_confidence=0.95)

        self.assertEqual(merged["source"], "merged")
        self.assertEqual(merged["worldwide_gross_usd"], 200_000_000)
        self.assertEqual(merged["india_net_cr"], 1050.0)
        self.assertEqual(merged["verdict"], "All-Time Blockbuster")
        self.assertEqual(merged["genre"], "Action, Thriller")
        self.assertEqual(merged["runtime_mins"], 175)
        self.assertEqual(merged["match_confidence"], 0.95)

    def test_merge_bom_only(self):
        bom = {"title_normalized": "test", "worldwide_gross_usd": 100}
        merged = merge_movie_data(bom, {})
        self.assertEqual(merged["worldwide_gross_usd"], 100)
        self.assertIsNone(merged.get("india_net_cr"))


if __name__ == "__main__":
    unittest.main()
