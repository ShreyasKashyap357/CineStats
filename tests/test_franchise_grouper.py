import unittest
import sqlite3
from src.db.init_db import _create_tables
from src.logic.franchise_grouper import FranchiseGrouper

class TestFranchiseGrouper(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        _create_tables(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_build_hierarchy(self):
        # Create a hierarchy: MCU -> Avengers -> Iron Man
        lowest_id = FranchiseGrouper.build_hierarchy(
            self.conn, 
            universe="Marvel Cinematic Universe", 
            franchise="The Avengers", 
            series="Iron Man"
        )
        self.assertIsNotNone(lowest_id)
        
        # Verify the nodes were created correctly
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name, parent_franchise_id, franchise_type FROM franchises")
        nodes = {row['name']: dict(row) for row in cursor.fetchall()}
        
        self.assertIn("Marvel Cinematic Universe", nodes)
        self.assertIn("The Avengers", nodes)
        self.assertIn("Iron Man", nodes)
        
        mcu = nodes["Marvel Cinematic Universe"]
        avengers = nodes["The Avengers"]
        iron_man = nodes["Iron Man"]
        
        self.assertIsNone(mcu['parent_franchise_id'])
        self.assertEqual(avengers['parent_franchise_id'], mcu['id'])
        self.assertEqual(iron_man['parent_franchise_id'], avengers['id'])
        
        self.assertEqual(mcu['franchise_type'], 'universe')
        self.assertEqual(iron_man['franchise_type'], 'series')
        
    def test_recalculate_cumulative_stats(self):
        # Build hierarchy
        series_id = FranchiseGrouper.build_hierarchy(
            self.conn, 
            universe="Test Universe", 
            franchise="Test Franchise", 
            series="Test Series"
        )
        
        # Add movies
        self.conn.execute("""
            INSERT INTO movies (title_normalized, worldwide_gross_usd, india_net_cr, release_date, franchise_id)
            VALUES 
            ('movie 1', 1000, 10, '2020-01-01', ?),
            ('movie 2', 500, 5, '2021-01-01', ?)
        """, (series_id, series_id))
        self.conn.commit()
        
        # Roll up
        FranchiseGrouper.recalculate_cumulative_stats(self.conn)
        
        # Check Series
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM franchises WHERE name = 'Test Series'")
        series = cursor.fetchone()
        
        self.assertEqual(series['cumulative_worldwide_usd'], 1500)
        self.assertEqual(series['cumulative_india_net_cr'], 15)
        self.assertEqual(series['total_entries'], 2)
        self.assertEqual(series['first_release'], '2020-01-01')
        self.assertEqual(series['latest_release'], '2021-01-01')
        
        # Check Universe (should have received rolled-up stats)
        cursor.execute("SELECT * FROM franchises WHERE name = 'Test Universe'")
        universe = cursor.fetchone()
        
        self.assertEqual(universe['cumulative_worldwide_usd'], 1500)
        self.assertEqual(universe['total_entries'], 2)

    def test_get_franchise_tree(self):
        # Build hierarchy
        FranchiseGrouper.build_hierarchy(self.conn, universe="U1", franchise="F1", series="S1")
        FranchiseGrouper.build_hierarchy(self.conn, universe="U1", franchise="F1", series="S2")
        FranchiseGrouper.build_hierarchy(self.conn, universe="U1", franchise="F2")
        
        # Retrieve U1 id
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM franchises WHERE name = 'U1'")
        u1_id = cursor.fetchone()['id']
        
        tree = FranchiseGrouper.get_franchise_tree(self.conn, u1_id)
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]['name'], "U1")
        self.assertEqual(len(tree[0]['children']), 2)
        
        # F1 should have 2 children
        f1 = next(child for child in tree[0]['children'] if child['name'] == 'F1')
        self.assertEqual(len(f1['children']), 2)

if __name__ == '__main__':
    unittest.main()
