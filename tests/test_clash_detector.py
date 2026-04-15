import unittest
import sqlite3
from src.db.init_db import _create_tables
from src.logic.clash_detector import ClashDetector, CLASH_TYPE_DIRECT, CLASH_TYPE_WINDOW

class TestClashDetector(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        _create_tables(self.conn)

        self.conn.executescript("""
            INSERT INTO movies (id, title_display, title_normalized, release_date, worldwide_gross_usd)
            VALUES
            -- Same-day pair (Barbenheimer)
            (1, 'Barbie',        'barbie',        '2023-07-21', 1400000000),
            (2, 'Oppenheimer',   'oppenheimer',   '2023-07-21',  950000000),
            -- Small movie on same day (below major-clash threshold)
            (3, 'Random Movie',  'random movie',  '2023-07-21',     500000),
            -- Released 10 days later → within 14-day window of Barbie
            (4, 'Window Film',   'window film',   '2023-07-31',  80000000),
            -- Released 30 days later → outside window
            (5, 'Far Away Film', 'far away film', '2023-08-20', 200000000);
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    # ── Per-movie lookup ─────────────────────────────────────────────────────

    def test_direct_clash_is_labelled(self):
        """Barbie should see Oppenheimer as a direct clash."""
        clashes = ClashDetector.get_clashing_movies(self.conn, 1)
        direct = [c for c in clashes if c['clash_type'] == CLASH_TYPE_DIRECT]
        titles = {c['title_display'] for c in direct}
        self.assertIn('Oppenheimer', titles)
        self.assertIn('Random Movie', titles)

    def test_window_clash_is_labelled(self):
        """Barbie should see Window Film as a release (window) clash."""
        clashes = ClashDetector.get_clashing_movies(self.conn, 1)
        window = [c for c in clashes if c['clash_type'] == CLASH_TYPE_WINDOW]
        titles = {c['title_display'] for c in window}
        self.assertIn('Window Film', titles)
        self.assertNotIn('Far Away Film', titles)

    def test_no_clashes_for_isolated_movie(self):
        """Far Away Film has nobody within 14 days."""
        clashes = ClashDetector.get_clashing_movies(self.conn, 5)
        self.assertEqual(len(clashes), 0)

    def test_custom_window_days(self):
        """Shrinking the window to 5 days should exclude Window Film from Barbie."""
        clashes = ClashDetector.get_clashing_movies(self.conn, 1, window_days=5)
        titles = {c['title_display'] for c in clashes}
        self.assertNotIn('Window Film', titles)
        # Direct clashes remain
        self.assertIn('Oppenheimer', titles)

    # ── Aggregate major clashes ──────────────────────────────────────────────

    def test_find_all_major_clashes_direct(self):
        """There is exactly one direct-clash date with major films."""
        df = ClashDetector.find_all_major_clashes(self.conn, min_gross_usd=10_000_000)
        direct = df[df['clash_type'] == CLASH_TYPE_DIRECT]
        self.assertEqual(len(direct), 1)
        row = direct.iloc[0]
        self.assertEqual(row['movie_count'], 2)
        self.assertIn('Barbie', row['clash_title'])
        self.assertIn('Oppenheimer', row['clash_title'])

    def test_find_all_major_clashes_window(self):
        """Window Film clashes with both Barbie and Oppenheimer (within 14 days)."""
        df = ClashDetector.find_all_major_clashes(self.conn, min_gross_usd=10_000_000)
        window = df[df['clash_type'] == CLASH_TYPE_WINDOW]
        # Window Film vs Barbie, Window Film vs Oppenheimer → 2 window pairs
        self.assertEqual(len(window), 2)
        all_titles = ' '.join(window['clash_title'].tolist())
        self.assertIn('Window Film', all_titles)

    def test_far_away_excluded_from_window(self):
        """Far Away Film (30 days later) should not appear in any window clash."""
        df = ClashDetector.find_all_major_clashes(self.conn, min_gross_usd=10_000_000)
        all_titles = ' '.join(df['clash_title'].tolist())
        self.assertNotIn('Far Away Film', all_titles)


if __name__ == '__main__':
    unittest.main()
