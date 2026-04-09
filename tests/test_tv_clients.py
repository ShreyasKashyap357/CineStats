"""Tests for TV/Anime Clients."""
import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.clients.jikan_client import _parse_anime_node
from src.clients.anilist_client import _parse_media_node
from src.clients.tvmaze_client import _parse_show_node


class TestClientParsers(unittest.TestCase):

    def test_jikan_parser(self):
        jikan_data = {
            "mal_id": 21,
            "title": "One Piece",
            "titles": [
                {"type": "English", "title": "One Piece"},
                {"type": "Japanese", "title": "ワンピース"}
            ],
            "score": 8.7,
            "rank": 50,
            "popularity": 20,
            "demographics": [{"name": "Shounen"}],
            "genres": [{"name": "Action"}, {"name": "Adventure"}],
            "studios": [{"name": "Toei Animation"}],
            "episodes": 1000,
            "images": {"jpg": {"large_image_url": "http://example.com/op.jpg"}}
        }
        
        parsed = _parse_anime_node(jikan_data)
        
        self.assertEqual(parsed["mal_id"], 21)
        self.assertEqual(parsed["title_display"], "One Piece")
        self.assertEqual(parsed["title_english"], "One Piece")
        self.assertEqual(parsed["mal_score"], 8.7)
        self.assertEqual(parsed["demographic"], "Shounen")
        self.assertEqual(parsed["genre"], "Action, Adventure")
        self.assertEqual(parsed["studio"], "Toei Animation")
        self.assertEqual(parsed["poster_url"], "http://example.com/op.jpg")

    def test_anilist_parser(self):
        anilist_data = {
            "id": 21,
            "idMal": 21,
            "title": {
                "romaji": "One Piece",
                "english": "One Piece",
                "native": "ワンピース"
            },
            "averageScore": 87,
            "popularity": 100000,
            "episodes": 1000,
            "status": "RELEASING"
        }
        
        parsed = _parse_media_node(anilist_data)
        
        self.assertEqual(parsed["anilist_id"], 21)
        self.assertEqual(parsed["mal_id"], 21)
        self.assertEqual(parsed["anilist_score"], 87)
        self.assertEqual(parsed["anilist_popularity"], 100000)

    def test_tvmaze_parser(self):
        tvmaze_data = {
            "id": 82,
            "name": "Game of Thrones",
            "genres": ["Drama", "Adventure", "Fantasy"],
            "status": "Ended",
            "premiered": "2011-04-17",
            "rating": {"average": 9.0},
            "network": {"name": "HBO", "country": {"code": "US"}}
        }
        
        parsed = _parse_show_node(tvmaze_data)
        
        self.assertEqual(parsed["tvmaze_id"], 82)
        self.assertEqual(parsed["title_display"], "Game of Thrones")
        self.assertEqual(parsed["genre"], "Drama, Adventure, Fantasy")
        self.assertEqual(parsed["network"], "HBO")
        self.assertEqual(parsed["origin_country"], "US")
        self.assertEqual(parsed["avg_rating"], 9.0)
        self.assertEqual(parsed["content_type"], "tv_series")


if __name__ == "__main__":
    unittest.main()
