# utils/billing.py
# Handles bill generation, GST calculation, and order storage (SQLite)

import sqlite3
import os
from datetime import datetime


# ── Constants ──────────────────────────────────────────────────────────────────
GST_RATE    = 0.08   # 8% GST
SERVICE_FEE = 2.00   # Flat service fee per order
DB_PATH     = os.path.join(os.path.dirname(__file__), "..", "data", "orders.db")


# ── Database Setup ─────────────────────────────────────────────────────────────
def init_db():
    """Create the orders table in SQLite if it doesn't exist."""
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT NOT NULL,
            items       TEXT NOT NULL,
            subtotal    REAL NOT NULL,
            gst         REAL NOT NULL,
            service_fee REAL NOT NULL,
            total       REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_order(order: dict, bill: dict):
    """
    Persist a completed order to the SQLite database.
    
    Args:
        order: Dict of ordered items {name: {quantity, price, ...}}
        bill: Dict with subtotal, gst, total
    """
    try:
        init_db()
        conn      = sqlite3.connect(DB_PATH)
        cursor    = conn.cursor()
        items_str = "; ".join([f"{name} x{d['quantity']}" for name, d in order.items()])

        cursor.execute("""
            INSERT INTO orders (timestamp, items, subtotal, gst, service_fee, total)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            items_str,
            bill["subtotal"],
            bill["gst"],
            bill["service_fee"],
            bill["total"]
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB save error: {e}")


def get_order_history(limit: int = 10) -> list:
    """
    Retrieve recent orders from the database.
    
    Args:
        limit: Max number of orders to return
        
    Returns:
        List of order dicts
    """
    try:
        init_db()
        conn   = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows    = cursor.fetchall()
        conn.close()
        columns = ["id", "timestamp", "items", "subtotal", "gst", "service_fee", "total"]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"DB read error: {e}")
        return []


# ── Bill Calculation ───────────────────────────────────────────────────────────
def calculate_bill(order: dict) -> dict:
    """
    Calculate the full itemized bill for an order.
    
    Args:
        order: Dict of {item_name: {"quantity": int, "price": float}}
        
    Returns:
        Bill dict with line items, subtotal, GST, service fee, and total
    """
    if not order:
        return {}

    line_items = []
    subtotal   = 0.0

    for item_name, details in order.items():
        qty      = details.get("quantity", 1)
        price    = details.get("price", 0.0)
        subtotal_item = qty * price
        subtotal     += subtotal_item

        line_items.append({
            "name":     item_name,
            "quantity": qty,
            "unit_price": price,
            "subtotal": subtotal_item
        })

    gst         = round(subtotal * GST_RATE, 2)
    service_fee = SERVICE_FEE
    total       = round(subtotal + gst + service_fee, 2)

    return {
        "line_items":   line_items,
        "subtotal":     round(subtotal, 2),
        "gst":          gst,
        "gst_rate":     f"{int(GST_RATE * 100)}%",
        "service_fee":  service_fee,
        "total":        total
    }


def format_bill_text(bill: dict) -> str:
    """
    Format the bill as a printable text receipt.
    
    Args:
        bill: Output from calculate_bill()
        
    Returns:
        Formatted string receipt
    """
    if not bill:
        return "No items to bill."

    lines = ["=" * 40, "       🍽️  BISTRO AI — RECEIPT", "=" * 40]

    for item in bill["line_items"]:
        name_str = f"{item['name']} x{item['quantity']}"
        price_str = f"${item['subtotal']:.2f}"
        # Right-align price
        padding = 40 - len(name_str) - len(price_str)
        lines.append(f"{name_str}{' ' * max(padding, 1)}{price_str}")

    lines.append("-" * 40)
    lines.append(f"Subtotal:{' ' * 23}${bill['subtotal']:.2f}")
    lines.append(f"GST ({bill['gst_rate']}):{' ' * 20}${bill['gst']:.2f}")
    lines.append(f"Service Fee:{' ' * 21}${bill['service_fee']:.2f}")
    lines.append("=" * 40)
    lines.append(f"TOTAL:{' ' * 27}${bill['total']:.2f}")
    lines.append("=" * 40)
    lines.append(f"  {datetime.now().strftime('%d %b %Y  %I:%M %p')}")
    lines.append("  Thank you for dining with us! 🙏")
    lines.append("=" * 40)

    return "\n".join(lines)
