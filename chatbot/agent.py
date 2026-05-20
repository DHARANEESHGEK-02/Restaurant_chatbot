# chatbot/agent.py
# The brain of the chatbot — connects LangChain, Mistral AI, memory, and RAG

import os
from langchain_mistralai import ChatMistralAI
from langchain.schema import HumanMessage, SystemMessage

from chatbot.prompts import SYSTEM_PROMPT, RECOMMENDATION_PROMPT, NUTRITION_ANALYSIS_PROMPT
from chatbot.retriever import retrieve_context
from chatbot.memory import format_history_for_prompt


def get_llm(api_key: str, temperature: float = 0.7):
    """
    Initialize the Mistral AI LLM via LangChain.
    
    Args:
        api_key: Your Mistral API key
        temperature: Controls creativity (0 = focused, 1 = creative)
    """
    return ChatMistralAI(
        model="mistral-large-latest",   # Best quality Mistral model
        mistral_api_key=api_key,
        temperature=temperature,
        max_tokens=1024
    )


def format_current_order(order: dict) -> str:
    """
    Convert the order dictionary into a readable string for the prompt.
    
    Args:
        order: Dict of {item_name: {"quantity": int, "price": float, ...}}
    """
    if not order:
        return "No items in cart yet."

    lines = []
    total = 0.0
    for item, details in order.items():
        qty   = details.get("quantity", 1)
        price = details.get("price", 0)
        subtotal = qty * price
        total   += subtotal
        lines.append(f"  • {item} x{qty}  →  ${subtotal:.2f}")

    lines.append(f"\n  Subtotal: ${total:.2f}")
    return "\n".join(lines)


def chat(user_message: str, api_key: str, current_order: dict) -> str:
    """
    Main chat function. Runs the full RAG pipeline:
    1. Retrieve relevant menu/FAQ context from FAISS
    2. Format conversation history
    3. Build prompt with context + history + order
    4. Call Mistral AI and return response
    
    Args:
        user_message: What the customer typed
        api_key: Mistral API key
        current_order: Items currently in cart
        
    Returns:
        AI assistant response string
    """
    try:
        # Step 1: Retrieve relevant context via RAG
        context = retrieve_context(user_message, k=5)

        # Step 2: Get formatted conversation history
        history = format_history_for_prompt(max_turns=8)

        # Step 3: Format current order for prompt
        order_text = format_current_order(current_order)

        # Step 4: Build the full prompt
        full_prompt = SYSTEM_PROMPT.format(
            context=context,
            chat_history=history,
            current_order=order_text,
            question=user_message
        )

        # Step 5: Call Mistral AI
        llm = get_llm(api_key)
        messages = [HumanMessage(content=full_prompt)]
        response = llm.invoke(messages)

        return response.content

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return "⚠️ Invalid API key. Please check your Mistral API key in the sidebar."
        elif "429" in error_msg:
            return "⚠️ Rate limit reached. Please wait a moment and try again."
        else:
            return f"⚠️ Something went wrong: {error_msg}\n\nPlease try again."


def get_recommendations(preference: str, api_key: str, current_order: dict) -> str:
    """
    Generate AI-powered food recommendations based on a preference.
    
    Args:
        preference: e.g., "high protein", "low calorie", "vegetarian"
        api_key: Mistral API key
        current_order: Items currently in cart
    """
    try:
        context    = retrieve_context(f"{preference} food menu", k=6)
        order_text = format_current_order(current_order)

        prompt = RECOMMENDATION_PROMPT.format(
            context=context,
            preference=preference,
            current_order=order_text
        )

        llm = get_llm(api_key, temperature=0.8)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content

    except Exception as e:
        return f"⚠️ Could not generate recommendations: {str(e)}"


def get_nutrition_analysis(order_items: list, nutrition_totals: dict, api_key: str) -> str:
    """
    Generate an AI health analysis of the current order.
    
    Args:
        order_items: List of item names in cart
        nutrition_totals: Dict with total calories, protein, carbs, fat
        api_key: Mistral API key
    """
    try:
        prompt = NUTRITION_ANALYSIS_PROMPT.format(
            order_items=", ".join(order_items),
            calories=nutrition_totals.get("calories", 0),
            protein=nutrition_totals.get("protein", 0),
            carbs=nutrition_totals.get("carbs", 0),
            fat=nutrition_totals.get("fat", 0)
        )

        llm = get_llm(api_key, temperature=0.5)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content

    except Exception as e:
        return f"⚠️ Could not analyze nutrition: {str(e)}"
