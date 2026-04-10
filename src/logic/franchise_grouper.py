"""
CineStats — Franchise Grouper
Section 5 of the v1.0 specification.

Implements the 3-level hierarchy logic for grouping entities:
Level 1: Cinematic Universe (e.g. Marvel Cinematic Universe)
Level 2: Franchise (e.g. The Avengers, Spider-Man)
Level 3: Series (e.g. Iron Man Trilogy)

Provides methods to map movies to these nodes and perform recursive 
cumulative aggregation of box office statistics up the tree.
"""
import sqlite3
from typing import Optional, Dict, Any, List

class FranchiseGrouper:
    @staticmethod
    def get_or_create_node(conn: sqlite3.Connection, name: str, franchise_type: str, parent_id: Optional[int] = None) -> int:
        """Fetch an existing franchise node or create it."""
        cursor = conn.cursor()
        name_normalized = name.lower().strip()
        
        # Check if exists
        query = "SELECT id FROM franchises WHERE name_normalized = ? AND franchise_type = ?"
        params = [name_normalized, franchise_type]
        if parent_id is not None:
            query += " AND parent_franchise_id = ?"
            params.append(parent_id)
        else:
            query += " AND parent_franchise_id IS NULL"
            
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if row:
            return row['id']
            
        # Create new
        cursor.execute(
            """INSERT INTO franchises (name, name_normalized, parent_franchise_id, franchise_type) 
               VALUES (?, ?, ?, ?)""",
            (name, name_normalized, parent_id, franchise_type)
        )
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def build_hierarchy(conn: sqlite3.Connection, universe: Optional[str] = None, 
                        franchise: Optional[str] = None, series: Optional[str] = None) -> Optional[int]:
        """
        Build or retrieve the chain of nodes.
        Returns the ID of the lowest specified level, to which a movie should be assigned.
        """
        parent_id = None
        
        if universe:
            parent_id = FranchiseGrouper.get_or_create_node(conn, universe, 'universe', parent_id)
            
        if franchise:
            parent_id = FranchiseGrouper.get_or_create_node(conn, franchise, 'franchise', parent_id)
            
        if series:
            parent_id = FranchiseGrouper.get_or_create_node(conn, series, 'series', parent_id)
            
        return parent_id

    @staticmethod
    def assign_movie(conn: sqlite3.Connection, movie_id: int, lowest_level_franchise_id: int):
        """Link a movie directly to a franchise node."""
        conn.execute("UPDATE movies SET franchise_id = ? WHERE id = ?", (lowest_level_franchise_id, movie_id))
        conn.commit()

    @staticmethod
    def recalculate_cumulative_stats(conn: sqlite3.Connection):
        """
        Roll up metrics from movies to Series, then Franchises, then Universes.
        Metrics: cumulative_worldwide_usd, cumulative_india_net_cr, first_release, latest_release, total_entries
        """
        cursor = conn.cursor()
        
        # 1. Reset all franchises
        cursor.execute('''
            UPDATE franchises SET 
                cumulative_worldwide_usd = 0,
                cumulative_india_net_cr = 0,
                total_entries = 0,
                first_release = NULL,
                latest_release = NULL
        ''')
        
        # 2. Rollup from movies directly assigned to ANY franchise level
        # A movie could be directly attached to a Series, Franchise, or Universe.
        cursor.execute('''
            SELECT franchise_id, 
                   COUNT(id) as cnt,
                   SUM(worldwide_gross_usd) as ww_gross,
                   SUM(india_net_cr) as ind_net,
                   MIN(release_date) as first_rel,
                   MAX(release_date) as latest_rel
            FROM movies 
            WHERE franchise_id IS NOT NULL
            GROUP BY franchise_id
        ''')
        
        movie_rollups = cursor.fetchall()
        for row in movie_rollups:
            cursor.execute('''
                UPDATE franchises SET 
                    cumulative_worldwide_usd = COALESCE(cumulative_worldwide_usd, 0) + COALESCE(?, 0),
                    cumulative_india_net_cr = COALESCE(cumulative_india_net_cr, 0) + COALESCE(?, 0),
                    total_entries = COALESCE(total_entries, 0) + ?,
                    first_release = CASE 
                        WHEN first_release IS NULL THEN ? 
                        WHEN ? < first_release THEN ? 
                        ELSE first_release END,
                    latest_release = CASE 
                        WHEN latest_release IS NULL THEN ? 
                        WHEN ? > latest_release THEN ? 
                        ELSE latest_release END
                WHERE id = ?
            ''', (
                row['ww_gross'], row['ind_net'], row['cnt'],
                row['first_rel'], row['first_rel'], row['first_rel'],
                row['latest_rel'], row['latest_rel'], row['latest_rel'],
                row['franchise_id']
            ))
            
        # 3. Bottom-up recursive rollup: Series -> Franchise -> Universe
        # We assume 3 levels max, so we can do it in passes: 
        # Pass 1: Series -> Franchise
        # Pass 2: Franchise -> Universe
        
        for child_type, parent_type in [('series', 'franchise'), ('franchise', 'universe')]:
            cursor.execute(f'''
                SELECT parent_franchise_id,
                       SUM(cumulative_worldwide_usd) as ww_gross,
                       SUM(cumulative_india_net_cr) as ind_net,
                       SUM(total_entries) as cnt,
                       MIN(first_release) as first_rel,
                       MAX(latest_release) as latest_rel
                FROM franchises
                WHERE franchise_type = ? AND parent_franchise_id IS NOT NULL
                GROUP BY parent_franchise_id
            ''', (child_type,))
            
            rollups = cursor.fetchall()
            for r in rollups:
                cursor.execute('''
                    UPDATE franchises SET 
                        cumulative_worldwide_usd = COALESCE(cumulative_worldwide_usd, 0) + COALESCE(?, 0),
                        cumulative_india_net_cr = COALESCE(cumulative_india_net_cr, 0) + COALESCE(?, 0),
                        total_entries = COALESCE(total_entries, 0) + ?,
                        first_release = CASE 
                            WHEN first_release IS NULL THEN ? 
                            WHEN ? < first_release THEN ? 
                            ELSE first_release END,
                        latest_release = CASE 
                            WHEN latest_release IS NULL THEN ? 
                            WHEN ? > latest_release THEN ? 
                            ELSE latest_release END
                    WHERE id = ?
                ''', (
                    r['ww_gross'], r['ind_net'], r['cnt'],
                    r['first_rel'], r['first_rel'], r['first_rel'],
                    r['latest_rel'], r['latest_rel'], r['latest_rel'],
                    r['parent_franchise_id']
                ))
                
        conn.commit()

    @staticmethod
    def get_franchise_tree(conn: sqlite3.Connection, universe_id: int) -> List[Dict[str, Any]]:
        """Return a nested dictionary representation of the universe -> franchise -> series tree."""
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get universe
        cursor.execute("SELECT * FROM franchises WHERE id = ?", (universe_id,))
        u_row = cursor.fetchone()
        if not u_row:
            return []
            
        universe = dict(u_row)
        universe['children'] = []
        
        # Get franchises
        cursor.execute("SELECT * FROM franchises WHERE parent_franchise_id = ?", (universe_id,))
        f_rows = cursor.fetchall()
        
        for f_row in f_rows:
            franchise = dict(f_row)
            franchise['children'] = []
            
            # Get series
            cursor.execute("SELECT * FROM franchises WHERE parent_franchise_id = ?", (f_row['id'],))
            s_rows = cursor.fetchall()
            for s_row in s_rows:
                franchise['children'].append(dict(s_row))
                
            universe['children'].append(franchise)
            
        return [universe]
