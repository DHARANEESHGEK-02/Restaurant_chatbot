# utils/recommendation.py
# Rule-based recommendation engine (used as fallback when AI is unavailable)

import pandas as pd
import os


MENU_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "menu.csv")


def load_menu() -> pd.DataFrame:
    return pd.read_csv(MENU_PATH)


def get_high_protein_items(n: int = 5) -> pd.DataFrame:
    """Return top N items by protein content."""
    df = load_menu()
    return df.nlargest(n, "protein")[["name", "category", "price", "protein", "calories"]]


def get_low_calorie_items(max_cal: int = 400, n: int = 5) -> pd.DataFrame:
    """Return items under a calorie threshold."""
    df = load_menu()
    return df[df["calories"] <= max_cal].nsmallest(n, "calories")[
        ["name", "category", "price", "calories", "protein"]
    ]


def get_vegetarian_items() -> pd.DataFrame:
    """Return all vegetarian items."""
    df = load_menu()
    return df[df["is_vegetarian"].str.lower() == "yes"][
        ["name", "category", "price", "calories", "health_score"]
    ]


def get_top_rated_items(n: int = 5) -> pd.DataFrame:
    """Return items with the highest health score."""
    df = load_menu()
    return df.nlargest(n, "health_score")[
        ["name", "category", "price", "health_score", "calories"]
    ]


def get_items_by_category(category: str) -> pd.DataFrame:
    """Return all items in a specific category."""
    df = load_menu()
    return df[df["category"].str.lower() == category.lower()][
        ["name", "price", "calories", "protein", "is_vegetarian", "health_score"]
    ]


def search_menu(query: str) -> pd.DataFrame:
    """
    Search menu by item name (case-insensitive partial match).
    
    Args:
        query: Search string
        
    Returns:
        Matching rows from the menu
    """
    df = load_menu()
    mask = df["name"].str.lower().str.contains(query.lower(), na=False)
    return df[mask][["name", "category", "price", "calories", "protein", "is_vegetarian"]]


def get_budget_friendly_items(max_price: float = 10.0, n: int = 5) -> pd.DataFrame:
    """Return healthy items under a price threshold."""
    df = load_menu()
    return df[df["price"] <= max_price].nlargest(n, "health_score")[
        ["name", "category", "price", "health_score", "calories"]
    ]
