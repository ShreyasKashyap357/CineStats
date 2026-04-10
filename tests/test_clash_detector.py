import unittest
import sqlite3
from src.db.init_db import _create_tables
from src.logic.clash_detector import ClashDetector

class TestClashDetector(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        _create_tables(self.conn)
        
        self.conn.executescript("""
            INSERT INTO movies (id, title_display, title_normalized, release_date, worldwide_gross_usd)
            VALUES 
            (1, 'Barbie', 'barbie', '2023-07-21', 1400000000),
            (2, 'Oppenheimer', 'oppenheimer', '2023-07-21', 950000000),
            (3, 'Random Movie', 'random movie', '2023-07-21', 500000),
            (4, 'No Clash', 'no clash', '2023-08-01', 50000000);
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_get_clashing_movies(self):
        clashes = ClashDetector.get_clashing_movies(self.conn, 1) # Barbie
        self.assertEqual(len(clashes), 2)
        
        # Ordered by worldwide gross DESC
        self.assertEqual(clashes[0]['title_display'], 'Oppenheimer')
        self.assertEqual(clashes[1]['title_display'], 'Random Movie')
        
        # Test no clashes
        clashes_none = ClashDetector.get_clashing_movies(self.conn, 4)
        self.assertEqual(len(clashes_none), 0)

    def test_find_all_major_clashes(self):
        # Min gross 10 million, should only consider Barbie and Oppenheimer
        df = ClashDetector.find_all_major_clashes(self.conn, min_gross_usd=10000000)
        self.assertFalse(df.empty)
        self.assertEqual(len(df), 1)
        row = df.iloc[0]
        self.assertEqual(row['movie_count'], 2)
        self.assertTrue('Barbie' in row['clash_title'])
        self.assertTrue('Oppenheimer' in row['clash_title'])
        self.assertFalse('Random Movie' in row['clash_title'])
        self.assertEqual(row['total_weekend_clash_usd'], 2350000000)

if __name__ == '__main__':
    unittest.main()
