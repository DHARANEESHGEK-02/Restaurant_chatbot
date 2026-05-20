# app.py
# 🍽️ Bistro AI — AI-Powered Restaurant Chatbot
# Entry point for the Streamlit application

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# ── Local imports ──────────────────────────────────────────────────────────────
from chatbot.agent    import chat, get_recommendations, get_nutrition_analysis
from chatbot.memory   import init_memory, add_message, get_chat_history, clear_memory
from chatbot.retriever import build_vector_store
from utils.billing    import calculate_bill, format_bill_text, save_order, get_order_history
from utils.nutrition  import get_nutrition_summary
from utils.recommendation import (
    load_menu, get_high_protein_items, get_low_calorie_items,
    get_vegetarian_items, get_top_rated_items, search_menu
)

# ── Load .env for local development ───────────────────────────────────────────
load_dotenv()

# ── Page Config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="Bistro AI 🍽️",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS — Custom Styling
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Fonts ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@400;500&display=swap');

/* ── Root palette ──────────────────────────────────── */
:root {
    --cream:   #FAF7F2;
    --brown:   #6B3F1E;
    --gold:    #D4A843;
    --green:   #3A7D44;
    --red:     #C0392B;
    --bg:      #1a1a1a;
    --card-bg: #242424;
    --border:  #333;
    --text:    #E8E4DC;
    --muted:   #888;
}

/* ── Global ────────────────────────────────────────── */
html, body, .stApp { background-color: var(--bg) !important; color: var(--text); }
h1, h2, h3         { font-family: 'Playfair Display', serif !important; }
p, div, span, label{ font-family: 'DM Sans', sans-serif !important; }

/* ── Sidebar ────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid var(--border);
}

/* ── Cards ──────────────────────────────────────────── */
.menu-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.menu-card:hover { border-color: var(--gold); }

/* ── Chat bubbles ───────────────────────────────────── */
.user-bubble {
    background: linear-gradient(135deg, #6B3F1E, #A0522D);
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 8px 0;
    max-width: 80%;
    margin-left: auto;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    line-height: 1.5;
}
.bot-bubble {
    background: var(--card-bg);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 8px 0;
    max-width: 80%;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    line-height: 1.5;
}

/* ── Metric boxes ───────────────────────────────────── */
.macro-box {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}
.macro-label { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
.macro-value { font-size: 26px; font-weight: 700; color: var(--gold); font-family: 'Playfair Display', serif; }
.macro-unit  { font-size: 13px; color: var(--muted); }

/* ── Badges ──────────────────────────────────────────── */
.badge-veg   { background:#1a3a1e; color:#4caf50; padding:2px 8px; border-radius:999px; font-size:12px; }
.badge-nonveg{ background:#3a1a1a; color:#ef9a9a; padding:2px 8px; border-radius:999px; font-size:12px; }
.badge-cat   { background:#2a2a1a; color:var(--gold); padding:2px 8px; border-radius:999px; font-size:12px; }

/* ── Health score bar ───────────────────────────────── */
.score-bar-bg  { background:#333; border-radius:999px; height:8px; }
.score-bar-fill{ background:linear-gradient(90deg,#c0392b,#d4a843,#3a7d44); border-radius:999px; height:8px; }

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

/* ── Section headers ─────────────────────────────────── */
.section-header {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    color: var(--gold);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* ── Cart item ───────────────────────────────────────── */
.cart-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    font-size: 14px;
}

/* ── Info box ────────────────────────────────────────── */
.info-box {
    background: #1a2a1a;
    border-left: 3px solid var(--green);
    padding: 10px 14px;
    border-radius: 4px;
    font-size: 14px;
    margin: 6px 0;
}
.warn-box {
    background: #2a1a0a;
    border-left: 3px solid var(--gold);
    padding: 10px 14px;
    border-radius: 4px;
    font-size: 14px;
    margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  Session State Initialization
# ══════════════════════════════════════════════════════════════════════════════
def init_session():
    """Initialize all session state variables on first load."""
    defaults = {
        "order":         {},       # {item_name: {quantity, price, calories, ...}}
        "page":          "Chat",   # Active sidebar page
        "api_key":       os.getenv("MISTRAL_API_KEY", ""),
        "vector_ready":  False,
        "order_placed":  False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    init_memory()   # Initialize chat history

init_session()


# ══════════════════════════════════════════════════════════════════════════════
#  Sidebar
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # Logo / branding
        st.markdown("""
        <div style='text-align:center; padding: 20px 0 10px;'>
            <div style='font-size:48px;'>🍽️</div>
            <div style='font-family:"Playfair Display",serif; font-size:22px; color:#D4A843; font-weight:700;'>
                Bistro AI
            </div>
            <div style='font-size:12px; color:#888; margin-top:4px;'>
                Your Smart Dining Assistant
            </div>
        </div>
        <hr style='border-color:#333; margin:12px 0;'>
        """, unsafe_allow_html=True)

        # Navigation
        pages = {
            "Chat":          "💬",
            "Menu":          "🍴",
            "My Order":      "🛒",
            "Nutrition":     "📊",
            "Recommendations":"⭐",
            "Order History": "📋",
        }
        st.markdown("<div style='font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Navigation</div>", unsafe_allow_html=True)
        for page, icon in pages.items():
            active = st.session_state.page == page
            style  = "background:#6B3F1E; color:white;" if active else "background:transparent; color:#E8E4DC;"
            if st.button(f"{icon}  {page}", key=f"nav_{page}", use_container_width=True):
                st.session_state.page = page
                st.rerun()

        st.markdown("<hr style='border-color:#333; margin:16px 0;'>", unsafe_allow_html=True)

        # API Key
        st.markdown("<div style='font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>Mistral API Key</div>", unsafe_allow_html=True)
        api_input = st.text_input(
            "API Key", value=st.session_state.api_key,
            type="password", label_visibility="collapsed",
            placeholder="Enter your Mistral API key..."
        )
        if api_input != st.session_state.api_key:
            st.session_state.api_key = api_input

        if st.session_state.api_key:
            st.markdown("<div style='color:#4caf50; font-size:12px;'>✅ API key set</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#ef9a9a; font-size:12px;'>⚠️ API key required for AI chat</div>", unsafe_allow_html=True)
            st.markdown("[Get free key →](https://console.mistral.ai)", unsafe_allow_html=True)

        # Build vector store button
        st.markdown("<hr style='border-color:#333; margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>RAG Setup</div>", unsafe_allow_html=True)
        if st.button("🔧 Build Vector Store", use_container_width=True):
            with st.spinner("Building FAISS index..."):
                try:
                    build_vector_store()
                    st.session_state.vector_ready = True
                    st.success("✅ Vector store ready!")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Cart summary
        if st.session_state.order:
            st.markdown("<hr style='border-color:#333; margin:16px 0;'>", unsafe_allow_html=True)
            total_items = sum(d["quantity"] for d in st.session_state.order.values())
            total_price = sum(d["quantity"] * d["price"] for d in st.session_state.order.values())
            st.markdown(f"""
            <div style='background:#242424; border:1px solid #333; border-radius:10px; padding:12px;'>
                <div style='font-size:12px; color:#888; margin-bottom:6px;'>CURRENT ORDER</div>
                <div style='font-size:18px; font-weight:700; color:#D4A843;'>{total_items} items</div>
                <div style='font-size:14px; color:#E8E4DC;'>Subtotal: ${total_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        # Reset session
        st.markdown("<hr style='border-color:#333; margin:16px 0;'>", unsafe_allow_html=True)
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.order = {}
            st.session_state.order_placed = False
            clear_memory()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  Page: Chat
# ══════════════════════════════════════════════════════════════════════════════
def render_chat_page():
    st.markdown("<div class='section-header'>💬 Chat with Bistro AI</div>", unsafe_allow_html=True)

    if not st.session_state.api_key:
        st.warning("⚠️ Please enter your Mistral API key in the sidebar to start chatting.")

    # Quick-start prompts
    st.markdown("<div style='font-size:13px; color:#888; margin-bottom:10px;'>Quick prompts:</div>", unsafe_allow_html=True)
    quick_cols = st.columns(4)
    quick_prompts = [
        "What's on the menu?",
        "I want something high protein",
        "Add a Grilled Chicken Salad",
        "What are today's healthy options?",
    ]
    for i, (col, prompt) in enumerate(zip(quick_cols, quick_prompts)):
        with col:
            if st.button(prompt, key=f"quick_{i}", use_container_width=True):
                _handle_user_message(prompt)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Chat history display
    chat_container = st.container()
    with chat_container:
        history = get_chat_history()
        if not history:
            st.markdown("""
            <div class='bot-bubble'>
                👋 Welcome to <strong>Bistro AI</strong>! I'm here to help you explore our menu,
                place orders, and find the perfect meal for you.<br><br>
                You can ask me things like:<br>
                • "Show me your healthy options"<br>
                • "Add a Caesar Salad to my order"<br>
                • "What's high in protein?"<br>
                • "What are your opening hours?"<br><br>
                What can I get started for you today? 🍽️
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in history:
                if msg["role"] == "user":
                    st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='bot-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

    # Input box
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        input_col, btn_col = st.columns([5, 1])
        with input_col:
            user_input = st.text_input(
                "Message", placeholder="Ask me anything about the menu, your order, nutrition...",
                label_visibility="collapsed"
            )
        with btn_col:
            submitted = st.form_submit_button("Send 🚀", use_container_width=True)

    if submitted and user_input.strip():
        _handle_user_message(user_input.strip())


def _handle_user_message(message: str):
    """Process user message: update order if needed, call AI, update history."""
    add_message("user", message)

    # ── Detect order intent (basic keyword matching) ───────────────────────────
    menu_df  = load_menu()
    msg_lower = message.lower()

    for _, row in menu_df.iterrows():
        item_name = row["name"]
        if item_name.lower() in msg_lower:
            if any(w in msg_lower for w in ["add", "order", "want", "get", "give me", "i'll have", "one more"]):
                # Determine quantity
                qty = 1
                for word, num in [("two", 2), ("three", 3), ("2", 2), ("3", 3)]:
                    if word in msg_lower:
                        qty = num
                        break
                # Add to order
                if item_name in st.session_state.order:
                    st.session_state.order[item_name]["quantity"] += qty
                else:
                    st.session_state.order[item_name] = {
                        "quantity": qty,
                        "price":    float(row["price"]),
                        "calories": int(row["calories"]),
                        "protein":  int(row["protein"]),
                        "carbs":    int(row["carbs"]),
                        "fat":      int(row["fat"]),
                    }
            elif any(w in msg_lower for w in ["remove", "cancel", "delete", "take off"]):
                if item_name in st.session_state.order:
                    del st.session_state.order[item_name]
            break

    # ── Call AI ────────────────────────────────────────────────────────────────
    if st.session_state.api_key:
        with st.spinner("Bistro AI is thinking..."):
            response = chat(message, st.session_state.api_key, st.session_state.order)
    else:
        response = (
            "⚠️ I need a Mistral API key to respond intelligently. "
            "Please add yours in the sidebar. "
            "\n\nIn the meantime, head to the **Menu** tab to browse our dishes, "
            "or **My Order** to manage your cart!"
        )

    add_message("assistant", response)
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  Page: Menu
# ══════════════════════════════════════════════════════════════════════════════
def render_menu_page():
    st.markdown("<div class='section-header'>🍴 Our Menu</div>", unsafe_allow_html=True)

    menu_df = load_menu()
    categories = ["All"] + sorted(menu_df["category"].unique().tolist())

    # Filters
    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 2])
    with filter_col1:
        selected_cat = st.selectbox("Category", categories)
    with filter_col2:
        veg_filter = st.selectbox("Diet", ["All", "Vegetarian", "Non-Vegetarian"])
    with filter_col3:
        search_query = st.text_input("Search", placeholder="e.g. chicken, salad...")

    # Apply filters
    filtered = menu_df.copy()
    if selected_cat != "All":
        filtered = filtered[filtered["category"] == selected_cat]
    if veg_filter == "Vegetarian":
        filtered = filtered[filtered["is_vegetarian"].str.lower() == "yes"]
    elif veg_filter == "Non-Vegetarian":
        filtered = filtered[filtered["is_vegetarian"].str.lower() == "no"]
    if search_query:
        filtered = filtered[filtered["name"].str.lower().str.contains(search_query.lower())]

    st.markdown(f"<div style='color:#888; font-size:13px; margin-bottom:16px;'>{len(filtered)} items found</div>", unsafe_allow_html=True)

    # Render cards in 3 columns
    cols = st.columns(3)
    for i, (_, row) in enumerate(filtered.iterrows()):
        with cols[i % 3]:
            veg_badge  = "<span class='badge-veg'>🌿 Veg</span>" if str(row["is_vegetarian"]).lower() == "yes" else "<span class='badge-nonveg'>🍖 Non-Veg</span>"
            cat_badge  = f"<span class='badge-cat'>{row['category']}</span>"
            score      = int(row["health_score"])
            score_pct  = score * 10  # out of 100

            st.markdown(f"""
            <div class='menu-card'>
                <div style='display:flex; justify-content:space-between; align-items:start; margin-bottom:8px;'>
                    <div>
                        {veg_badge} &nbsp; {cat_badge}
                    </div>
                    <div style='font-size:20px; font-weight:700; color:#D4A843;'>${row['price']}</div>
                </div>
                <div style='font-family:"Playfair Display",serif; font-size:17px; font-weight:600; margin-bottom:6px;'>{row['name']}</div>
                <div style='font-size:12px; color:#888; margin-bottom:10px;'>{row['health_benefits']}</div>
                <div style='display:grid; grid-template-columns:1fr 1fr 1fr 1fr; gap:4px; margin-bottom:10px;'>
                    <div style='text-align:center; background:#2a2a2a; border-radius:6px; padding:4px;'>
                        <div style='font-size:11px; color:#888;'>Cal</div>
                        <div style='font-size:13px; font-weight:600;'>{row['calories']}</div>
                    </div>
                    <div style='text-align:center; background:#2a2a2a; border-radius:6px; padding:4px;'>
                        <div style='font-size:11px; color:#888;'>Protein</div>
                        <div style='font-size:13px; font-weight:600;'>{row['protein']}g</div>
                    </div>
                    <div style='text-align:center; background:#2a2a2a; border-radius:6px; padding:4px;'>
                        <div style='font-size:11px; color:#888;'>Carbs</div>
                        <div style='font-size:13px; font-weight:600;'>{row['carbs']}g</div>
                    </div>
                    <div style='text-align:center; background:#2a2a2a; border-radius:6px; padding:4px;'>
                        <div style='font-size:11px; color:#888;'>Fat</div>
                        <div style='font-size:13px; font-weight:600;'>{row['fat']}g</div>
                    </div>
                </div>
                <div style='margin-bottom:6px;'>
                    <div style='display:flex; justify-content:space-between; font-size:12px; color:#888; margin-bottom:3px;'>
                        <span>Health Score</span><span>{score}/10</span>
                    </div>
                    <div class='score-bar-bg'>
                        <div class='score-bar-fill' style='width:{score_pct}%;'></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Add to order button
            if st.button(f"+ Add to Order", key=f"add_{row['name']}", use_container_width=True):
                name = row["name"]
                if name in st.session_state.order:
                    st.session_state.order[name]["quantity"] += 1
                else:
                    st.session_state.order[name] = {
                        "quantity": 1,
                        "price":    float(row["price"]),
                        "calories": int(row["calories"]),
                        "protein":  int(row["protein"]),
                        "carbs":    int(row["carbs"]),
                        "fat":      int(row["fat"]),
                    }
                st.toast(f"✅ Added {name} to your order!", icon="🛒")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  Page: My Order
# ══════════════════════════════════════════════════════════════════════════════
def render_order_page():
    st.markdown("<div class='section-header'>🛒 My Order</div>", unsafe_allow_html=True)

    if not st.session_state.order:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; color:#555;'>
            <div style='font-size:64px;'>🛒</div>
            <div style='font-size:18px; margin-top:12px;'>Your cart is empty</div>
            <div style='font-size:14px; margin-top:6px;'>Head to the Menu tab to add items!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    order_col, bill_col = st.columns([3, 2])

    with order_col:
        st.markdown("**Order Items**")
        for item_name, details in list(st.session_state.order.items()):
            qty       = details["quantity"]
            unit_price = details["price"]
            cols = st.columns([3, 1, 1, 1])
            with cols[0]:
                st.markdown(f"<div style='padding:8px 0; font-size:15px;'>{item_name}</div>", unsafe_allow_html=True)
            with cols[1]:
                new_qty = st.number_input("Qty", min_value=0, max_value=20, value=qty, key=f"qty_{item_name}", label_visibility="collapsed")
                if new_qty != qty:
                    if new_qty == 0:
                        del st.session_state.order[item_name]
                    else:
                        st.session_state.order[item_name]["quantity"] = new_qty
                    st.rerun()
            with cols[2]:
                st.markdown(f"<div style='padding:8px 0; color:#D4A843;'>${unit_price * qty:.2f}</div>", unsafe_allow_html=True)
            with cols[3]:
                if st.button("🗑️", key=f"del_{item_name}"):
                    del st.session_state.order[item_name]
                    st.rerun()
            st.markdown("<hr style='margin:0; border-color:#333;'>", unsafe_allow_html=True)

    with bill_col:
        bill = calculate_bill(st.session_state.order)
        st.markdown("**Bill Summary**")
        st.markdown(f"""
        <div style='background:#242424; border:1px solid #333; border-radius:12px; padding:20px;'>
            <div style='display:flex; justify-content:space-between; padding:6px 0; color:#888; font-size:14px;'>
                <span>Subtotal</span><span>${bill['subtotal']:.2f}</span>
            </div>
            <div style='display:flex; justify-content:space-between; padding:6px 0; color:#888; font-size:14px;'>
                <span>GST ({bill['gst_rate']})</span><span>${bill['gst']:.2f}</span>
            </div>
            <div style='display:flex; justify-content:space-between; padding:6px 0; color:#888; font-size:14px;'>
                <span>Service Fee</span><span>${bill['service_fee']:.2f}</span>
            </div>
            <hr style='border-color:#444; margin:10px 0;'>
            <div style='display:flex; justify-content:space-between; padding:6px 0; font-size:20px; font-weight:700; color:#D4A843;'>
                <span>Total</span><span>${bill['total']:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        if st.button("✅ Place Order", use_container_width=True, type="primary"):
            save_order(st.session_state.order, bill)
            st.session_state.order_placed = True
            # Add confirmation to chat
            items_str = ", ".join(st.session_state.order.keys())
            add_message("assistant", f"🎉 Your order has been placed! Items: {items_str}. Total: ${bill['total']:.2f}. Thank you for dining with us!")
            st.session_state.order = {}
            st.success("🎉 Order placed successfully!")
            st.balloons()

        if st.button("🗑️ Clear Cart", use_container_width=True):
            st.session_state.order = {}
            st.rerun()

        # Print receipt
        receipt_text = format_bill_text(bill)
        st.download_button("📄 Download Receipt", receipt_text, file_name="bistro_receipt.txt", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  Page: Nutrition
# ══════════════════════════════════════════════════════════════════════════════
def render_nutrition_page():
    st.markdown("<div class='section-header'>📊 Nutrition Dashboard</div>", unsafe_allow_html=True)

    if not st.session_state.order:
        st.info("🛒 Add items to your order to see a nutrition breakdown.")
        return

    summary = get_nutrition_summary(st.session_state.order)
    totals  = summary["totals"]
    daily   = summary["daily_percentage"]

    # ── Macro cards ────────────────────────────────────────────────────────────
    st.markdown("#### Total Macronutrients")
    m1, m2, m3, m4 = st.columns(4)
    macros = [
        (m1, "🔥 Calories", totals["calories"], "kcal",  daily["calories"]),
        (m2, "💪 Protein",  totals["protein"],  "g",     daily["protein"]),
        (m3, "🌾 Carbs",    totals["carbs"],    "g",     daily["carbs"]),
        (m4, "🫒 Fat",      totals["fat"],      "g",     daily["fat"]),
    ]
    for col, label, val, unit, pct in macros:
        with col:
            color = "#4caf50" if pct <= 80 else ("#D4A843" if pct <= 120 else "#ef9a9a")
            st.markdown(f"""
            <div class='macro-box'>
                <div class='macro-label'>{label}</div>
                <div class='macro-value'>{val}</div>
                <div class='macro-unit'>{unit}</div>
                <div style='margin-top:8px; font-size:12px; color:{color};'>
                    {pct}% of daily recommended
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Progress bars ──────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.markdown("#### Daily Value Coverage")

    for label, pct in [("Calories", daily["calories"]), ("Protein", daily["protein"]),
                        ("Carbs", daily["carbs"]), ("Fat", daily["fat"])]:
        capped = min(pct, 100)
        color  = "#3A7D44" if pct <= 80 else ("#D4A843" if pct <= 120 else "#C0392B")
        st.markdown(f"""
        <div style='margin-bottom:12px;'>
            <div style='display:flex; justify-content:space-between; font-size:13px; margin-bottom:4px;'>
                <span>{label}</span><span style='color:{color};'>{pct}% of daily</span>
            </div>
            <div style='background:#333; border-radius:999px; height:10px;'>
                <div style='background:{color}; border-radius:999px; height:10px; width:{capped}%; transition:width 0.5s;'></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Health warnings ────────────────────────────────────────────────────────
    warnings = summary["warnings"]
    if warnings:
        st.markdown("#### Health Insights")
        for w in warnings:
            box_class = "info-box" if "✅" in w or "💪" in w else "warn-box"
            st.markdown(f"<div class='{box_class}'>{w}</div>", unsafe_allow_html=True)

    # ── Diet suitability ───────────────────────────────────────────────────────
    st.markdown("#### Diet Suitability")
    d1, d2, d3, d4 = st.columns(4)
    diet_cols = [d1, d2, d3, d4]
    for i, (diet, (suitable, reason)) in enumerate(summary["diet_suitability"].items()):
        with diet_cols[i]:
            color = "#1a3a1e" if suitable else "#3a1a1a"
            border = "#4caf50" if suitable else "#ef9a9a"
            st.markdown(f"""
            <div style='background:{color}; border:1px solid {border}; border-radius:10px; padding:14px; text-align:center;'>
                <div style='font-size:13px; font-weight:600; color:#E8E4DC; margin-bottom:6px;'>{diet}</div>
                <div style='font-size:12px; color:#aaa;'>{reason}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── AI Analysis ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    if st.session_state.api_key:
        if st.button("🤖 Get AI Health Analysis", use_container_width=True):
            with st.spinner("Analyzing your meal..."):
                analysis = get_nutrition_analysis(
                    list(st.session_state.order.keys()), totals, st.session_state.api_key
                )
            st.markdown(f"<div class='bot-bubble'>{analysis}</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  Page: Recommendations
# ══════════════════════════════════════════════════════════════════════════════
def render_recommendations_page():
    st.markdown("<div class='section-header'>⭐ Food Recommendations</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🤖 AI Recommendations", "📋 Quick Picks"])

    with tab1:
        if not st.session_state.api_key:
            st.warning("⚠️ Enter your Mistral API key in the sidebar to get AI recommendations.")
        else:
            pref_options = [
                "High protein meals for muscle gain",
                "Low calorie meals for weight loss",
                "Vegetarian healthy options",
                "Balanced meals for energy",
                "Budget-friendly healthy meals",
                "Quick light lunch options",
            ]
            col1, col2 = st.columns([3, 1])
            with col1:
                pref = st.selectbox("Select your preference", pref_options)
            with col2:
                custom_pref = st.text_input("Or type custom", placeholder="e.g. diabetic-friendly")

            final_pref = custom_pref if custom_pref else pref

            if st.button("🚀 Get Recommendations", use_container_width=True, type="primary"):
                with st.spinner("Finding the best options for you..."):
                    recs = get_recommendations(final_pref, st.session_state.api_key, st.session_state.order)
                st.markdown(f"<div class='bot-bubble'>{recs}</div>", unsafe_allow_html=True)

    with tab2:
        picks = {
            "💪 High Protein":   get_high_protein_items(5),
            "🥗 Low Calorie":    get_low_calorie_items(400, 5),
            "🌿 Vegetarian":     get_vegetarian_items().head(5),
            "⭐ Healthiest":     get_top_rated_items(5),
        }
        for label, df in picks.items():
            st.markdown(f"**{label}**")
            if df.empty:
                st.markdown("<div style='color:#888; font-size:13px;'>No items found.</div>", unsafe_allow_html=True)
            else:
                # Clean display
                display_df = df.rename(columns={
                    "name": "Item", "price": "Price ($)", "calories": "Calories",
                    "protein": "Protein (g)", "health_score": "Health Score",
                    "is_vegetarian": "Vegetarian", "carbs": "Carbs (g)"
                })
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  Page: Order History
# ══════════════════════════════════════════════════════════════════════════════
def render_history_page():
    st.markdown("<div class='section-header'>📋 Order History</div>", unsafe_allow_html=True)

    history = get_order_history(limit=20)

    if not history:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; color:#555;'>
            <div style='font-size:64px;'>📋</div>
            <div style='font-size:18px; margin-top:12px;'>No orders yet</div>
            <div style='font-size:14px; margin-top:6px;'>Place your first order to see history here!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    total_spent = sum(o["total"] for o in history)
    h1, h2, h3 = st.columns(3)
    with h1:
        st.metric("Total Orders", len(history))
    with h2:
        st.metric("Total Spent", f"${total_spent:.2f}")
    with h3:
        st.metric("Avg Order Value", f"${total_spent/len(history):.2f}")

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    for order in history:
        with st.expander(f"Order #{order['id']}  —  {order['timestamp']}  —  **${order['total']:.2f}**"):
            st.markdown(f"**Items:** {order['items']}")
            bc1, bc2, bc3 = st.columns(3)
            bc1.metric("Subtotal", f"${order['subtotal']:.2f}")
            bc2.metric("GST",      f"${order['gst']:.2f}")
            bc3.metric("Total",    f"${order['total']:.2f}")


# ══════════════════════════════════════════════════════════════════════════════
#  Main App Router
# ══════════════════════════════════════════════════════════════════════════════
def main():
    render_sidebar()

    page = st.session_state.page
    if   page == "Chat":            render_chat_page()
    elif page == "Menu":            render_menu_page()
    elif page == "My Order":        render_order_page()
    elif page == "Nutrition":       render_nutrition_page()
    elif page == "Recommendations": render_recommendations_page()
    elif page == "Order History":   render_history_page()


if __name__ == "__main__":
    main()
