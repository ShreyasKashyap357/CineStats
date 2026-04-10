import unittest
import sqlite3
from src.db.init_db import _create_tables
from src.logic.mover_calculator import MoverCalculator

class TestMoverCalculator(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        _create_tables(self.conn)
        
        self.conn.executescript("""
            INSERT INTO movies (id, title_display, title_normalized) VALUES 
            (1, 'Growing Movie', 'growing movie'),
            (2, 'Dropping Movie', 'dropping movie'),
            (3, 'Tiny Movie', 'tiny movie');
            
            INSERT INTO daily_performance (movie_id, date, daily_gross_usd) VALUES
            -- Growing (+50%)
            (1, '2023-01-01', 200000),
            (1, '2023-01-02', 300000),
            -- Dropping (-50%)
            (2, '2023-01-01', 500000),
            (2, '2023-01-02', 250000),
            -- Tiny Movie (+200%, but under min_gross threshold)
            (3, '2023-01-01', 10000),
            (3, '2023-01-02', 30000);
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_get_daily_movers(self):
        # Using default min_gross=100000
        df = MoverCalculator.get_daily_movers(self.conn, '2023-01-02')
        self.assertFalse(df.empty)
        
        # Should only have Growing and Dropping movies
        self.assertEqual(len(df), 2)
        
        # Highest % change first
        self.assertEqual(df.iloc[0]['title_display'], 'Growing Movie')
        self.assertEqual(df.iloc[0]['pct_change'], 50.0)
        
        self.assertEqual(df.iloc[1]['title_display'], 'Dropping Movie')
        self.assertEqual(df.iloc[1]['pct_change'], -50.0)

    def test_get_top_gainers_and_losers(self):
        res = MoverCalculator.get_top_gainers_and_losers(self.conn, '2023-01-02')
        gainers = res['gainers']
        losers = res['losers']
        
        self.assertEqual(len(gainers), 1)
        self.assertEqual(gainers.iloc[0]['title_display'], 'Growing Movie')
        
        self.assertEqual(len(losers), 1)
        self.assertEqual(losers.iloc[0]['title_display'], 'Dropping Movie')
        self.assertEqual(losers.iloc[0]['pct_change'], -50.0)

if __name__ == '__main__':
    unittest.main()
