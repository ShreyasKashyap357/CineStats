"""
CineStats — Similar Title Recommender
Section 5 of the v1.0 specification.

Provides content-based recommendation logic. Uses rule-based scoring 
based on shared franchise, exact genre overlap, release decade, and language.
"""
import sqlite3
from typing import List, Dict, Any

class SimilarTitleRecommender:
    @staticmethod
    def get_similar_movies(conn: sqlite3.Connection, movie_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Returns a list of similar movies for a given movie_id based on a weighted scoring algorithm.
        Score weights: 
        - Same franchise: +50
        - Same language: +20
        - Shared genre tags: +10 per tag
        """
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Fetch target movie details
        cursor.execute("SELECT franchise_id, language, genre FROM movies WHERE id = ?", (movie_id,))
        target = cursor.fetchone()
        
        if not target:
            return []
            
        t_franchise = target['franchise_id']
        t_language = target['language']
        t_genres = [g.strip().lower() for g in target['genre'].split(',')] if target['genre'] else []
        
        # 2. Fetch all other movies to score (in a real app, we'd pre-calculate or use vector embeddings, 
        # but for SQLite scale with <1M rows, heuristic scoring in memory or SQL is fine)
        # To make it efficient, we only score movies that share AT LEAST ONE attribute (language, franchise, or first genre)
        
        first_genre = t_genres[0] if t_genres else ""
        
        query = """
            SELECT id, title_display, franchise_id, language, genre, verdict
            FROM movies
            WHERE id != ?
              AND (franchise_id = ? OR language = ? OR genre LIKE ?)
        """
        
        cursor.execute(query, (movie_id, t_franchise, t_language, f"%{first_genre}%"))
        candidates = cursor.fetchall()
        
        # 3. Score candidates
        scored_candidates = []
        for c in candidates:
            score = 0
            
            if t_franchise and c['franchise_id'] == t_franchise:
                score += 50
                
            if t_language and c['language'] == t_language:
                score += 20
                
            c_genres = [g.strip().lower() for g in c['genre'].split(',')] if c['genre'] else []
            shared_genres = set(t_genres).intersection(set(c_genres))
            score += len(shared_genres) * 10
            
            if score > 0:
                sc = dict(c)
                sc['similarity_score'] = score
                scored_candidates.append(sc)
                
        # 4. Sort by score descending, then return top N
        scored_candidates.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored_candidates[:limit]
