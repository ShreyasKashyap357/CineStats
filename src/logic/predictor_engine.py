"""
CineStats — Predictor Engine
Section 5 of the v1.0 specification.

Implements opening-weekend to lifetime gross multiplier models.
Provides basic prediction for ongoing theatrical releases based on 
genre, language, or overall averages from historic data.
"""
import sqlite3
import pandas as pd
from typing import Optional, Dict

class PredictorEngine:
    @staticmethod
    def calculate_actual_multiplier(opening: float, lifetime: float) -> Optional[float]:
        """Calculate the exact multiplier for a film."""
        if not opening or opening <= 0 or not lifetime:
            return None
        return round(lifetime / opening, 2)

    @staticmethod
    def get_average_multipliers(conn: sqlite3.Connection) -> pd.DataFrame:
        """
        Calculates historical average multipliers grouped by genre and language.
        Only uses movies that have finished their theatrical run (assumed if days_in_release > 60 or verdict is set).
        """
        query = """
            SELECT genre, language, worldwide_gross_usd, opening_weekend_usd
            FROM movies
            WHERE opening_weekend_usd > 0 
              AND worldwide_gross_usd > 0
              AND (days_in_release IS NULL OR days_in_release > 60)
        """
        df = pd.read_sql(query, conn)
        
        if df.empty:
            return pd.DataFrame()
            
        df['multiplier'] = df['worldwide_gross_usd'] / df['opening_weekend_usd']
        
        # We can group by genre to find averages
        # To simplify, we split genres (since they might be comma-separated like "Action, Thriller")
        # For an MVP predictor, we can just take the first genre tag
        df['primary_genre'] = df['genre'].apply(lambda x: x.split(',')[0].strip() if x else 'Unknown')
        
        genre_avg = df.groupby('primary_genre')['multiplier'].agg(['mean', 'count']).reset_index()
        genre_avg = genre_avg[genre_avg['count'] > 2] # Requires at least 3 films for a stable average
        
        return genre_avg

    @staticmethod
    def predict_lifetime(conn: sqlite3.Connection, opening: float, 
                         genre: str = None, fallback_multiplier: float = 2.5) -> float:
        """
        Predict lifetime gross based on opening weekend and matching historical averages.
        Uses a fallback multiplier if insufficient historical data exists.
        """
        if not opening or opening <= 0:
            return 0.0
            
        multiplier = fallback_multiplier
        
        if genre:
            primary_genre = genre.split(',')[0].strip()
            df = PredictorEngine.get_average_multipliers(conn)
            if not df.empty and primary_genre in df['primary_genre'].values:
                # Extract the mean multiplier for this genre
                genre_mult = df[df['primary_genre'] == primary_genre]['mean'].iloc[0]
                multiplier = genre_mult
        
        predicted_gross = opening * multiplier
        return round(predicted_gross, 2)

    @staticmethod
    def update_predictions_for_running_films(conn: sqlite3.Connection):
        """
        We don't strictly save predictions to DB in v1.0, but this function 
        could apply predictions to 'currently in theatres' views dynamically.
        """
        pass
