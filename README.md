<<<<<<< HEAD
# 🍽️ Bistro AI — AI-Powered Restaurant Chatbot

> A smart, full-featured restaurant assistant built with **Streamlit**, **LangChain**, **Mistral AI**, and **FAISS** — featuring conversational ordering, real-time nutrition analysis, RAG-powered responses, and SQLite order history.

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **AI Chatbot** | Conversational assistant powered by Mistral AI with conversation memory |
| 🍴 **Menu Browser** | Filter by category, diet type, and search — with nutrition cards |
| 🛒 **Smart Ordering** | Add/remove items via chat or UI; live cart with quantity controls |
| 💳 **Bill Generation** | Itemized bill with GST + service fee; downloadable receipt |
| 📊 **Nutrition Dashboard** | Total macros, daily % coverage, diet suitability, health warnings |
| ⭐ **AI Recommendations** | Personalized meal suggestions based on health goals |
| 🧠 **RAG (Retrieval-Augmented Generation)** | FAISS vector search over menu + FAQ for accurate responses |
| 🗄️ **Order History** | Persistent order history stored in SQLite |
| 🔍 **Memory** | Bot remembers your conversation context across the session |

---

## 🗂️ Project Structure

```
restaurant_chatbot/
│
├── app.py                        # Main Streamlit app — UI + routing
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── .env.example                  # Environment variable template
├── .gitignore
│
├── .streamlit/
│   └── config.toml               # Streamlit theme + server settings
│
├── chatbot/
│   ├── __init__.py
│   ├── agent.py                  # LLM calls — chat, recommendations, analysis
│   ├── prompts.py                # System prompts for Mistral AI
│   ├── memory.py                 # ConversationBufferMemory (session state)
│   └── retriever.py              # FAISS vector store — build + query
│
├── data/
│   ├── __init__.py
│   ├── menu.csv                  # 27 menu items with full nutrition data
│   ├── nutrients.csv             # Daily recommended nutrient reference
│   ├── faq.csv                   # 20 restaurant FAQs
│   └── orders.db                 # SQLite order history (auto-created)
│
├── utils/
│   ├── __init__.py
│   ├── billing.py                # Bill calculation + SQLite storage
│   ├── nutrition.py              # Macro totals, warnings, diet suitability
│   └── recommendation.py        # Rule-based item filtering (fallback)
│
├── vector_db/
│   ├── __init__.py
│   └── faiss_index/              # FAISS index files (auto-generated)
│
└── static/                       # Static assets (images, icons)
    └── __init__.py
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourname/bistro-ai.git
cd bistro-ai/restaurant_chatbot
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your Mistral API key
```bash
cp .env.example .env
# Edit .env and add your key:
# MISTRAL_API_KEY=your_key_here
```
> Get a free key at [console.mistral.ai](https://console.mistral.ai)

### 5. Run the app
```bash
streamlit run app.py
```

### 6. Build the vector store (first time only)
Click **"🔧 Build Vector Store"** in the sidebar — this indexes the menu and FAQ into FAISS for RAG.

---

## 🤖 How It Works

```
User Message
     │
     ▼
┌─────────────────┐
│  FAISS Retriever│  ← Searches menu + FAQ for relevant context
└────────┬────────┘
         │  Top-K documents
         ▼
┌─────────────────┐
│  Prompt Builder │  ← Injects context + chat history + current order
└────────┬────────┘
         │  Full prompt
         ▼
┌─────────────────┐
│   Mistral AI    │  ← Generates intelligent, context-aware response
└────────┬────────┘
         │  Response
         ▼
┌─────────────────┐
│  Memory Store   │  ← Saves to session history (ConversationBufferMemory)
└─────────────────┘
```

---

## 📡 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit 1.35 |
| **LLM** | Mistral AI (`mistral-large-latest`) |
| **Orchestration** | LangChain 0.2 |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` |
| **Vector DB** | FAISS (CPU) |
| **Database** | SQLite (via Python `sqlite3`) |
| **Data** | CSV (menu, FAQ, nutrients) |

---

## ☁️ Deployment

### Streamlit Cloud
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select your repo → `app.py`
4. Add `MISTRAL_API_KEY` in **Secrets**

### Hugging Face Spaces
1. Create a new Space → SDK: **Streamlit**
2. Upload all files
3. Add `MISTRAL_API_KEY` in **Space Secrets**

### Render
1. Create a new **Web Service** → connect GitHub repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `streamlit run app.py --server.port $PORT`
4. Add `MISTRAL_API_KEY` as an environment variable

---

## 💬 Example Conversations

```
You:     What's on the menu?
Bot:     Here's an overview of our menu categories: Salads, Bowls, Wraps...

You:     I want something high protein for muscle gain
Bot:     Great goal! Here are our top protein-packed options:
         1. Grilled Chicken Salad — 35g protein, only 320 calories...

You:     Add a Grilled Chicken Salad and a Green Detox Juice
Bot:     Got it! I've added:
         • Grilled Chicken Salad x1 — $12.99
         • Green Detox Juice x1 — $5.99
         Your order total is $18.98. Anything else?

You:     Actually add one more salad
Bot:     Done! Updated your Grilled Chicken Salad to x2. Total is now $31.97.
```

---

## 📄 License

MIT License — feel free to use, modify, and deploy for personal or commercial projects.

---

## 🙏 Acknowledgements

- [Mistral AI](https://mistral.ai) for the powerful open-weight LLM
- [LangChain](https://langchain.com) for LLM orchestration
- [Streamlit](https://streamlit.io) for the rapid UI framework
- [FAISS](https://faiss.ai) by Meta for vector similarity search
- [HuggingFace](https://huggingface.co) for the sentence transformer embeddings
=======
# Restaurant_chatbot
>>>>>>> 5a92393cca887c84e7205e929a10585af275780b
