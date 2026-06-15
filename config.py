"""
Configuration constants for the Intelligent Maintenance Wizard.
All tunable parameters and model settings are centralized here.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MANUALS_DIR = DATA_DIR / "manuals"
SOPS_DIR = DATA_DIR / "sops"
LOGS_DIR = DATA_DIR / "logs"
SENSOR_DIR = DATA_DIR / "sensor_data"
SPARE_PARTS_DIR = DATA_DIR / "spare_parts"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"
MODELS_DIR = PROJECT_ROOT / "analytics" / "models"
FEEDBACK_DB = PROJECT_ROOT / "feedback.db"

# ──────────────────────────────────────────────
# LLM Configuration
# ──────────────────────────────────────────────
# For HuggingFace Inference API (free / pro tier)
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_PRIMARY_MODEL = os.getenv("HF_PRIMARY_MODEL", "Qwen/Qwen2.5-7B-Instruct")
HF_ROUTER_MODEL = os.getenv("HF_ROUTER_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
HF_INFERENCE_URL = "https://api-inference.huggingface.co/models/"

# For local hosting (Ollama)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_PRIMARY_MODEL = os.getenv("OLLAMA_PRIMARY_MODEL", "llama3:latest")
OLLAMA_ROUTER_MODEL = os.getenv("OLLAMA_ROUTER_MODEL", "llama3.2:latest")

# ──────────────────────────────────────────────
# Choose inference mode: "huggingface", "ollama", "groq", or "gemini"
# Defaults to "groq" — set GROQ_API_KEY below (or in .env) to use it
# out-of-the-box without touching the sidebar.
# ──────────────────────────────────────────────
INFERENCE_MODE = os.getenv("INFERENCE_MODE", "groq")

# ──────────────────────────────────────────────
# Groq (free tier for open-source models)
# DEFAULT KEY: put your key in a .env file as GROQ_API_KEY=... (recommended,
# and make sure .env is in .gitignore so it never gets committed/shared).
# Get a free key at https://console.groq.com/keys
# The sidebar field can still override this per-session.
# ──────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_PRIMARY_MODEL = os.getenv("GROQ_PRIMARY_MODEL", "llama-3.3-70b-versatile")
GROQ_ROUTER_MODEL = os.getenv("GROQ_ROUTER_MODEL", "llama-3.1-8b-instant")

# ──────────────────────────────────────────────
# Google Gemini (fallback option)
# DEFAULT KEY: Set GEMINI_API_KEY in your .env file (recommended), or replace
# "PASTE_YOUR_GEMINI_API_KEY_HERE" below directly. Either way, the app's
# sidebar field can still override this at runtime per-session.
# Get a free key at https://aistudio.google.com/apikey
# Using 1.5-flash models — generally more available free-tier quota
# than 2.0-flash on newly created API keys.
# ──────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "PASTE_YOUR_GEMINI_API_KEY_HERE")
GEMINI_PRIMARY_MODEL = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-1.5-flash")
GEMINI_ROUTER_MODEL = os.getenv("GEMINI_ROUTER_MODEL", "gemini-1.5-flash-8b")

# ──────────────────────────────────────────────
# Embedding Configuration
# ──────────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# ──────────────────────────────────────────────
# RAG Configuration
# ──────────────────────────────────────────────
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RETRIEVAL = 5
MAX_CONTEXT_TOKENS = 3000

# Collection names in ChromaDB
COLLECTIONS = {
    "manuals": "equipment_manuals",
    "sops": "standard_operating_procedures",
    "logs": "maintenance_logs",
    "failure_reports": "failure_analysis_reports",
}

# ──────────────────────────────────────────────
# Analytics Configuration
# ──────────────────────────────────────────────
ANOMALY_CONTAMINATION = 0.05  # Expected anomaly rate
ANOMALY_THRESHOLD = -0.5  # Isolation Forest threshold
LSTM_AE_SEQUENCE_LENGTH = 50
LSTM_AE_HIDDEN_DIM = 64
LSTM_AE_EPOCHS = 50
RUL_SEQUENCE_LENGTH = 30
RUL_HIDDEN_DIM = 128

# ──────────────────────────────────────────────
# Agent Configuration
# ──────────────────────────────────────────────
MAX_REVISION_LOOPS = 2
AGENT_TEMPERATURE = 0.1
AGENT_MAX_TOKENS = 2048

# ──────────────────────────────────────────────
# Equipment Registry (dynamic — backed by JSON)
# ──────────────────────────────────────────────
EQUIPMENT_REGISTRY_FILE = DATA_DIR / "equipment_registry.json"

_DEFAULT_EQUIPMENT = {
    "BF-001": {"name": "Blast Furnace #1", "type": "Blast Furnace", "criticality": "critical"},
    "BF-002": {"name": "Blast Furnace #2", "type": "Blast Furnace", "criticality": "critical"},
    "BOF-001": {"name": "Basic Oxygen Furnace #1", "type": "BOF", "criticality": "critical"},
    "BOF-002": {"name": "Basic Oxygen Furnace #2", "type": "BOF", "criticality": "high"},
    "RM-001": {"name": "Hot Rolling Mill #1", "type": "Rolling Mill", "criticality": "high"},
    "RM-002": {"name": "Cold Rolling Mill #1", "type": "Rolling Mill", "criticality": "high"},
    "RM-003": {"name": "Rolling Mill Motor #3", "type": "Rolling Mill", "criticality": "medium"},
    "CC-001": {"name": "Continuous Caster #1", "type": "Caster", "criticality": "critical"},
    "CC-002": {"name": "Continuous Caster #2", "type": "Caster", "criticality": "high"},
    "LF-001": {"name": "Ladle Furnace #1", "type": "Ladle Furnace", "criticality": "high"},
    "LF-002": {"name": "Ladle Furnace #2", "type": "Ladle Furnace", "criticality": "medium"},
}


def _load_equipment_registry() -> dict:
    """Load equipment registry from JSON, seeding it with defaults on first run."""
    import json
    if EQUIPMENT_REGISTRY_FILE.exists():
        try:
            with open(EQUIPMENT_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # First run — seed the file with defaults
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(EQUIPMENT_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(_DEFAULT_EQUIPMENT, f, indent=2)
    return dict(_DEFAULT_EQUIPMENT)


EQUIPMENT = _load_equipment_registry()  # snapshot at import time (back-compat)


def get_equipment() -> dict:
    """Always returns the current equipment registry from disk (no restart needed)."""
    return _load_equipment_registry()


# ──────────────────────────────────────────────
# Sensor Configuration
# ──────────────────────────────────────────────
# Sensor parameters per equipment type
SENSOR_PARAMS = {
    "Blast Furnace": ["temperature", "pressure", "gas_flow", "burden_level", "cooling_water_temp", "vibration"],
    "BOF": ["temperature", "oxygen_flow", "pressure", "vibration", "lance_position", "current"],
    "Rolling Mill": ["temperature", "vibration", "rpm", "torque", "oil_pressure", "current"],
    "Caster": ["temperature", "casting_speed", "mold_level", "cooling_water_flow", "vibration", "current"],
    "Ladle Furnace": ["temperature", "arc_voltage", "current", "pressure", "slag_height", "vibration"],
}

# Normal operating ranges (mean, std) per sensor per equipment type
SENSOR_RANGES = {
    "Blast Furnace": {
        "temperature": (1200, 50), "pressure": (2.5, 0.3), "gas_flow": (4500, 200),
        "burden_level": (85, 5), "cooling_water_temp": (35, 3), "vibration": (2.5, 0.5),
    },
    "BOF": {
        "temperature": (1650, 80), "oxygen_flow": (600, 30), "pressure": (1.8, 0.2),
        "vibration": (3.0, 0.6), "lance_position": (1.5, 0.1), "current": (450, 30),
    },
    "Rolling Mill": {
        "temperature": (350, 25), "vibration": (4.0, 0.8), "rpm": (1200, 50),
        "torque": (8500, 500), "oil_pressure": (45, 3), "current": (380, 25),
    },
    "Caster": {
        "temperature": (1550, 60), "casting_speed": (1.2, 0.1), "mold_level": (75, 3),
        "cooling_water_flow": (850, 40), "vibration": (1.8, 0.3), "current": (250, 20),
    },
    "Ladle Furnace": {
        "temperature": (1580, 70), "arc_voltage": (250, 15), "current": (35000, 2000),
        "pressure": (0.5, 0.05), "slag_height": (15, 2), "vibration": (2.0, 0.4),
    },
}

# ──────────────────────────────────────────────
# UI Configuration
# ──────────────────────────────────────────────
APP_TITLE = "🏭 Intelligent Maintenance Wizard"
APP_SUBTITLE = "Steel Manufacturing | Agentic AI-Powered Decision Support"
PAGE_ICON = "🏭"
LAYOUT = "wide"