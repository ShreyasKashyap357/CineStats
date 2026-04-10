import unittest
import sqlite3
from src.db.init_db import _create_tables
from src.logic.similar_title_recommender import SimilarTitleRecommender

class TestSimilarTitleRecommender(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        
        # We need a dummy schema for this test because similar title recommender accesses 'poster_url' etc.
        # But wait, our init_db movies table doesn't have poster_url yet. It was added in the v1.0 PDF changes list!
        # I'll just use the full schema creation to avoid missing columns if they were updated.
        _create_tables(self.conn)
        
        # If poster_url is missing in movies, let's add it manually since it's required by the query.
        try:
            self.conn.execute("ALTER TABLE movies ADD COLUMN poster_url TEXT")
        except sqlite3.OperationalError:
            pass # Already exists
            
        self.conn.executescript("""
            INSERT INTO movies (id, title_display, title_normalized, franchise_id, language, genre) VALUES 
            (1, 'Avengers: Endgame', 'avengers endgame', 1, 'English', 'Action, Sci-Fi'),
            (2, 'Avengers: Infinity War', 'avengers infinity war', 1, 'English', 'Action, Sci-Fi'),
            (3, 'Spider-Man', 'spiderman', 99, 'English', 'Action, Adventure'),
            (4, 'Indian Romance', 'indian romance', NULL, 'Hindi', 'Romance, Drama'),
            (5, 'Random English Movie', 'random', NULL, 'English', 'Comedy');
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_get_similar_movies(self):
        rec = SimilarTitleRecommender.get_similar_movies(self.conn, 1)
        
        # We expect Infinity War to be #1 (same franchise = 50, same lang = 20, same 2 genres = 20 -> score 90)
        # Spider-Man to be #2 (diff franchise = 0, same lang = 20, same 1 genre = 10 -> score 30)
        # Random English Movie to be #3 (diff franchise = 0, same lang = 20, same 0 genres = 0 -> score 20)
        # Indian Romance should score 0 and not be returned, or score 0 and be at bottom.
        
        self.assertTrue(len(rec) > 0)
        self.assertEqual(rec[0]['title_display'], 'Avengers: Infinity War')
        self.assertEqual(rec[0]['similarity_score'], 90)
        
        self.assertEqual(rec[1]['title_display'], 'Spider-Man')
        self.assertEqual(rec[1]['similarity_score'], 30)
        
        self.assertEqual(rec[2]['title_display'], 'Random English Movie')
        self.assertEqual(rec[2]['similarity_score'], 20)
        
        # Test movie with no overlaps except empty
        rec_hindi = SimilarTitleRecommender.get_similar_movies(self.conn, 4)
        self.assertEqual(len(rec_hindi), 0) # Nobody shares Hindi, Romance, Drama or franchise

if __name__ == '__main__':
    unittest.main()
