import unittest
import sqlite3
import pandas as pd
from src.db.init_db import _create_tables
from src.logic.predictor_engine import PredictorEngine

class TestPredictorEngine(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        _create_tables(self.conn)
        
        # Insert historical data
        self.conn.executescript("""
            INSERT INTO movies (title_normalized, genre, opening_weekend_usd, worldwide_gross_usd, days_in_release)
            VALUES 
            ('movie 1', 'Action, Sci-Fi', 100, 300, 100), -- mult: 3.0
            ('movie 2', 'Action, Adventure', 50, 125, 100), -- mult: 2.5
            ('movie 3', 'Action', 200, 400, 100), -- mult: 2.0 (avg Action mult: 2.5)
            ('movie 4', 'Horror', 10, 50, 100), -- mult: 5.0
            ('movie 5', 'Horror', 20, 80, 100), -- mult: 4.0
            ('movie 6', 'Horror', 5, 25, 100); -- mult: 5.0 (avg Horror mult: 4.66)
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_calculate_actual_multiplier(self):
        self.assertEqual(PredictorEngine.calculate_actual_multiplier(100, 300), 3.0)
        self.assertEqual(PredictorEngine.calculate_actual_multiplier(50, 125), 2.5)
        self.assertIsNone(PredictorEngine.calculate_actual_multiplier(0, 100))
        self.assertIsNone(PredictorEngine.calculate_actual_multiplier(100, 0))

    def test_get_average_multipliers(self):
        df = PredictorEngine.get_average_multipliers(self.conn)
        self.assertFalse(df.empty)
        
        # Action group (3 movies)
        action_row = df[df['primary_genre'] == 'Action']
        self.assertFalse(action_row.empty)
        self.assertAlmostEqual(action_row['mean'].iloc[0], 2.5)
        
        # Horror group (3 movies)
        horror_row = df[df['primary_genre'] == 'Horror']
        self.assertFalse(horror_row.empty)
        self.assertAlmostEqual(horror_row['mean'].iloc[0], 4.67, places=2)

    def test_predict_lifetime(self):
        # Action genre uses average 2.5
        predicted_action = PredictorEngine.predict_lifetime(self.conn, opening=100, genre="Action, Comedy")
        self.assertEqual(predicted_action, 250.0)
        
        # Horror genre uses average ~4.66
        predicted_horror = PredictorEngine.predict_lifetime(self.conn, opening=10, genre="Horror")
        self.assertAlmostEqual(predicted_horror, 46.66, places=1)
        
        # Unknown genre uses fallback 2.5
        predicted_unknown = PredictorEngine.predict_lifetime(self.conn, opening=100, genre="Romance", fallback_multiplier=3.0)
        self.assertEqual(predicted_unknown, 300.0)

if __name__ == '__main__':
    unittest.main()
