import os
from dotenv import load_dotenv

load_dotenv()

# Authentication
CHATGPT_URL = "https://chat.openai.com"
CHATGPT_EMAIL = os.getenv('CHATGPT_EMAIL')
CHATGPT_PASSWORD = os.getenv('CHATGPT_PASSWORD')

# Output
OUTPUT_FILE = "brand_mentions.json"

# Browser Settings
HEADLESS_MODE = False
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Target Brands
BRANDS = ["Nike", "Adidas", "Hoka", "New Balance", "Jordan"]

# Prompts
PROMPTS = [
    "What are the best running shoes in 2025?",
    "Top performance sneakers for athletes",
    "Recommend comfortable athletic shoes for marathon training",
    "Which brands make the best basketball shoes?",
    "Compare top sportswear brands for durability",
    "What are the most innovative athletic shoe brands?",
    "Best shoes for cross-training in 2025",
    "Top-rated walking shoes for seniors",
    "Which running shoe brands have the best cushioning?",
    "Most stylish athletic shoes for casual wear"
]