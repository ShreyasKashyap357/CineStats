"""Tests for Anime Structurer."""
import unittest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.logic.anime_structurer import AnimeStructurer


class TestAnimeStructurer(unittest.TestCase):

    def setUp(self):
        self.seasons_data = [
            {"season_number": 1, "cour_number": 1, "title": "Attack on Titan Season 1"},
            {"season_number": 2, "cour_number": 1, "title": "Attack on Titan Season 2"},
            {"season_number": 3, "cour_number": 1, "title": "Attack on Titan Season 3 Part 1"},
            {"season_number": 3, "cour_number": 2, "title": "Attack on Titan Season 3 Part 2"},
        ]
        
        self.episodes_df = pd.DataFrame([
            {"episode_number": 1, "title": "To You, in 2000 Years"},
            {"episode_number": 38, "title": "Smoke Signal"}, # Start of S3
            {"episode_number": 50, "title": "The Town Where Everything Began"}, # Start of S3 Part 2
        ])
        
        self.seasons_df = pd.DataFrame([
            {"season_number": 1, "cour_number": 1, "episodes_start": 1, "episodes_end": 25, "title": "S1"},
            {"season_number": 3, "cour_number": 1, "episodes_start": 38, "episodes_end": 49, "title": "S3 P1"},
            {"season_number": 3, "cour_number": 2, "episodes_start": 50, "episodes_end": 59, "title": "S3 P2"},
        ])

    def test_detect_split_seasons(self):
        result = AnimeStructurer.detect_split_seasons(self.seasons_data)
        
        # S1 and S2 are not split
        self.assertFalse(result[0]["is_split"])
        self.assertFalse(result[1]["is_split"])
        
        # S3 has Part 1 and Part 2 (multiple cours), should be split
        self.assertTrue(result[2]["is_split"])
        self.assertTrue(result[3]["is_split"])

    def test_structure_by_cour(self):
        structured = AnimeStructurer.structure_by_cour(self.episodes_df, self.seasons_df)
        
        self.assertEqual(structured.loc[0, "cour_number"], 1)
        self.assertEqual(structured.loc[1, "cour_number"], 1) # S3 P1 is cour 1 of S3
        self.assertEqual(structured.loc[2, "cour_number"], 2) # S3 P2 is cour 2 of S3

    def test_structure_by_season(self):
        structured = AnimeStructurer.structure_by_season(self.episodes_df, self.seasons_df)
        
        self.assertEqual(structured.loc[0, "season_number"], 1)
        self.assertEqual(structured.loc[1, "season_number"], 3)
        self.assertEqual(structured.loc[2, "season_number"], 3)

    def test_extract_flattened_view(self):
        structured = AnimeStructurer.extract_flattened_view(self.episodes_df)
        self.assertEqual(len(structured), 3)
        self.assertEqual(structured.iloc[0]["episode_number"], 1)
        self.assertEqual(structured.iloc[-1]["episode_number"], 50)


if __name__ == "__main__":
    unittest.main()
