"""Moteur de recommandation de structure de dashboard (mémoire MSc Data Management)."""

from .mining import build_rules, load_grid
from .recommender import recommander

__all__ = ["build_rules", "load_grid", "recommander"]
