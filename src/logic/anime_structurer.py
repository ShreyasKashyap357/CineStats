"""
CineStats — Anime Structurer
Business logic for Anime grouping (Cour, Season, Arc) and split-season detection.
Spec 10.1 (Anime Grouping Views).
"""
from typing import List, Dict, Any
import pandas as pd


class AnimeStructurer:
    
    @staticmethod
    def detect_split_seasons(seasons_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify if an anime has split seasons based on cour names or season gaps.
        
        Args:
            seasons_data: List of season dictionaries.
            
        Returns:
            List of season dictionaries with an updated `is_split` boolean flag.
        """
        # Basic split detection algorithm:
        # If multiple cours have the same season_number but different cour_numbers, it's a split season.
        # Another indicator is titles like "Season 2 Part 2".
        
        season_cour_map = {}
        for s in seasons_data:
            s_num = s.get("season_number")
            c_num = s.get("cour_number")
            title = s.get("title", "").lower()
            
            s["is_split"] = False
            
            if s_num is not None:
                if s_num not in season_cour_map:
                    season_cour_map[s_num] = []
                season_cour_map[s_num].append(s)
                
            if "part 2" in title or "part 3" in title or "cour 2" in title:
                 s["is_split"] = True

        # Mark all cours in a split season
        for s_num, cours in season_cour_map.items():
            if len(cours) > 1:
                for c in cours:
                    c["is_split"] = True
                    
        return seasons_data

    @staticmethod
    def structure_by_cour(episodes: pd.DataFrame, seasons: pd.DataFrame) -> pd.DataFrame:
        """Structure episodes grouped by specific production Cours."""
        if episodes.empty or seasons.empty:
            return episodes
        
        # Merge eps with seasons based on episode numbers
        # Typically seasons df defines episodes_start, episodes_end
        def get_cour_info(ep_num):
            for _, s in seasons.iterrows():
                if s['episodes_start'] <= ep_num <= s['episodes_end']:
                    return s['cour_number'], s['title']
            return None, None

        structured = episodes.copy()
        structured['cour_number'], structured['cour_title'] = zip(*structured['episode_number'].apply(get_cour_info))
        return structured

    @staticmethod
    def structure_by_season(episodes: pd.DataFrame, seasons: pd.DataFrame) -> pd.DataFrame:
        """Structure episodes grouped by Season."""
        if episodes.empty or seasons.empty:
            return episodes

        def get_season_info(ep_num):
            for _, s in seasons.iterrows():
                if s['episodes_start'] <= ep_num <= s['episodes_end']:
                    return s['season_number'], f"Season {s['season_number']}"
            return None, None

        structured = episodes.copy()
        structured['season_number'], structured['season_title'] = zip(*structured['episode_number'].apply(get_season_info))
        return structured

    @staticmethod
    def structure_by_arc(episodes: pd.DataFrame, arcs: pd.DataFrame) -> pd.DataFrame:
        """Structure episodes grouped by narrative Story Arcs."""
        if episodes.empty or arcs.empty:
            return episodes

        def get_arc_info(ep_num):
            for _, arc in arcs.iterrows():
                if arc['episodes_start'] <= ep_num <= arc['episodes_end']:
                    return arc['arc_name']
            return None

        structured = episodes.copy()
        structured['arc_name'] = structured['episode_number'].apply(get_arc_info)
        return structured

    @staticmethod
    def extract_flattened_view(structured_df: pd.DataFrame) -> pd.DataFrame:
        """Flattens a multi-cour / split series into continuous numbering."""
        if structured_df.empty:
            return structured_df
        # If it has a continuous episode_number, we just sort by it
        return structured_df.sort_values(by="episode_number").reset_index(drop=True)
