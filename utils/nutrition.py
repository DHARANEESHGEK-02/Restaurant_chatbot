# utils/nutrition.py
# Calculate total nutrition for an order and generate health insights

import pandas as pd
import os


# ── Constants ──────────────────────────────────────────────────────────────────
MENU_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "menu.csv")

# Recommended Daily Intake (average adult)
DAILY_CALORIES = 2000
DAILY_PROTEIN  = 50    # grams
DAILY_CARBS    = 275   # grams
DAILY_FAT      = 78    # grams


def load_menu() -> pd.DataFrame:
    """Load the menu CSV into a DataFrame."""
    return pd.read_csv(MENU_PATH)


def calculate_order_nutrition(order: dict) -> dict:
    """
    Sum up total macros for all items in the order.
    
    Args:
        order: {item_name: {"quantity": int, ...}}
        
    Returns:
        Dict with total calories, protein, carbs, fat
    """
    menu_df = load_menu()
    totals  = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

    for item_name, details in order.items():
        qty  = details.get("quantity", 1)
        row  = menu_df[menu_df["name"].str.lower() == item_name.lower()]
        if not row.empty:
            totals["calories"] += int(row["calories"].values[0]) * qty
            totals["protein"]  += int(row["protein"].values[0]) * qty
            totals["carbs"]    += int(row["carbs"].values[0]) * qty
            totals["fat"]      += int(row["fat"].values[0]) * qty

    return totals


def get_daily_percentage(totals: dict) -> dict:
    """
    Calculate what percentage of daily recommended values the order covers.
    
    Args:
        totals: Output from calculate_order_nutrition()
        
    Returns:
        Dict with % of daily recommended intake for each macro
    """
    return {
        "calories": round((totals["calories"] / DAILY_CALORIES) * 100, 1),
        "protein":  round((totals["protein"]  / DAILY_PROTEIN)  * 100, 1),
        "carbs":    round((totals["carbs"]    / DAILY_CARBS)    * 100, 1),
        "fat":      round((totals["fat"]      / DAILY_FAT)      * 100, 1),
    }


def get_health_warnings(totals: dict) -> list:
    """
    Return a list of health warning messages based on the order's nutrition.
    
    Args:
        totals: Output from calculate_order_nutrition()
        
    Returns:
        List of warning strings
    """
    warnings = []

    if totals["calories"] > DAILY_CALORIES:
        warnings.append(f"⚠️ This meal exceeds the daily recommended calorie intake ({DAILY_CALORIES} kcal).")
    elif totals["calories"] > DAILY_CALORIES * 0.75:
        warnings.append(f"📊 This meal covers {round(totals['calories']/DAILY_CALORIES*100)}% of daily calories — quite filling!")

    if totals["fat"] > DAILY_FAT * 0.8:
        warnings.append("🧈 High fat content. Consider pairing with a light drink or salad.")

    if totals["protein"] >= 40:
        warnings.append("💪 Excellent protein content — great for muscle maintenance and satiety.")

    if totals["carbs"] < 30:
        warnings.append("⚡ Low carb meal — good for low-carb or keto goals.")
    elif totals["carbs"] > 200:
        warnings.append("🍞 High carb content. Good for active days or post-workout recovery.")

    if totals["calories"] < 400:
        warnings.append("🥗 Light meal — consider adding a protein item or healthy side.")

    return warnings


def get_diet_suitability(totals: dict) -> dict:
    """
    Determine which common diet goals this meal is suitable for.
    
    Returns:
        Dict of {diet_name: (bool suitable, str reason)}
    """
    return {
        "Weight Loss":   (
            totals["calories"] < 600,
            "✅ Under 600 kcal" if totals["calories"] < 600 else "❌ Too high in calories"
        ),
        "Muscle Gain":   (
            totals["protein"] >= 30,
            "✅ 30g+ protein" if totals["protein"] >= 30 else "❌ Needs more protein"
        ),
        "Low Carb/Keto": (
            totals["carbs"] < 50,
            "✅ Under 50g carbs" if totals["carbs"] < 50 else "❌ Too high in carbs"
        ),
        "Balanced Diet": (
            300 <= totals["calories"] <= 800 and totals["protein"] >= 15,
            "✅ Well-balanced macros" if (300 <= totals["calories"] <= 800 and totals["protein"] >= 15)
            else "⚠️ Adjust for balance"
        ),
    }


def get_nutrition_summary(order: dict) -> dict:
    """
    Full nutrition analysis for an order — combines all the above functions.
    
    Returns:
        Dict with totals, daily%, warnings, diet_suitability
    """
    if not order:
        return {}

    totals     = calculate_order_nutrition(order)
    daily_pct  = get_daily_percentage(totals)
    warnings   = get_health_warnings(totals)
    diet_suit  = get_diet_suitability(totals)

    return {
        "totals":            totals,
        "daily_percentage":  daily_pct,
        "warnings":          warnings,
        "diet_suitability":  diet_suit
    }
