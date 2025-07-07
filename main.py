# deepseek_scraper.py
import asyncio
from playwright.async_api import async_playwright
import json
from collections import defaultdict
import os
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DEEPSEEK_URL = "https://chat.deepseek.com"
LOGIN_URL = "https://chat.deepseek.com/login"  # DeepSeek login page
EMAIL = os.getenv('DEEPSEEK_EMAIL')  # From .env file
PASSWORD = os.getenv('DEEPSEEK_PASSWORD')  # From .env file
OUTPUT_FILE = "brand_mentions.json"
HEADLESS_MODE = False  # Set to True for production after testing

# Sportswear brands to track
BRANDS = ["Nike", "Adidas", "Hoka", "New Balance", "Jordan"]

# Sample prompts about sportswear
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

async def setup_stealth_browser():
    """Configure browser to avoid detection"""
    playwright = await async_playwright().start()
    
    browser = await playwright.chromium.launch(
        headless=HEADLESS_MODE,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu"
        ],
        slow_mo=random.randint(100, 500)  # Random delays between actions
    )
    
    # Create context with stealth settings
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York",
        color_scheme="dark"
    )
    
    # Disable WebDriver detection
    await context.add_init_script("""
        delete Object.getPrototypeOf(navigator).webdriver;
        window.navigator.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    """)
    
    return playwright, browser, context

async def human_like_interaction(page):
    """Simulate human-like behavior"""
    await page.mouse.move(
        random.randint(0, 500),
        random.randint(0, 500),
        steps=random.randint(5, 20)
    )
    await page.wait_for_timeout(random.randint(200, 800))

async def login_to_deepseek(page):
    """Handle DeepSeek login with retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await page.goto(LOGIN_URL, wait_until="networkidle")
            await page.wait_for_timeout(random.randint(1000, 3000))
            
            # Check if already logged in
            if "chat" in page.url.lower():
                return True
                
            # Fill email
            email_field = await page.query_selector("input[type='email']")
            if not email_field:
                email_field = await page.query_selector("input[name='email']")
            
            if email_field:
                await human_like_interaction(page)
                await email_field.fill(EMAIL)
                await page.wait_for_timeout(random.randint(500, 1500))
                
                # Click continue/submit button
                continue_btn = await page.query_selector("button[type='submit']")
                if not continue_btn:
                    continue_btn = await page.query_selector("button:has-text('Continue')")
                
                if continue_btn:
                    await continue_btn.click()
                    await page.wait_for_timeout(2000)
            
            # Fill password if required
            password_field = await page.query_selector("input[type='password']")
            if password_field:
                await human_like_interaction(page)
                await password_field.fill(PASSWORD)
                await page.wait_for_timeout(random.randint(500, 1500))
                
                # Click login button
                login_btn = await page.query_selector("button[type='submit']")
                if not login_btn:
                    login_btn = await page.query_selector("button:has-text('Login')")
                
                if login_btn:
                    await login_btn.click()
                    await page.wait_for_timeout(3000)
            
            # Check for successful login
            await page.wait_for_url("**/chat**", timeout=15000)
            return True
            
        except Exception as e:
            print(f"Login attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                await page.wait_for_timeout(5000)
                continue
            raise Exception(f"Failed to login after {max_retries} attempts")

async def send_prompt_and_get_response(page, prompt):
    """Send a prompt to DeepSeek and return the response"""
    # Find input field (DeepSeek might use different selectors)
    input_selectors = [
        "textarea",
        "[contenteditable='true']",
        "input[type='text']",
        ".input-box"
    ]
    
    input_field = None
    for selector in input_selectors:
        input_field = await page.query_selector(selector)
        if input_field:
            break
    
    if not input_field:
        raise Exception("Could not find input field")
    
    # Human-like typing
    await input_field.click()
    await page.wait_for_timeout(random.randint(200, 500))
    
    for char in prompt:
        await input_field.press(char)
        await page.wait_for_timeout(random.randint(30, 150))
    
    await page.keyboard.press("Enter")
    
    # Wait for response (adjust selectors as needed)
    try:
        await page.wait_for_selector(".stop-generating-button", timeout=120000, state="attached")
        await page.wait_for_selector(".stop-generating-button", timeout=120000, state="detached")
    except:
        pass  # Continue even if we don't see the stop button
    
    # Get the last response (adjust selectors as needed)
    response_selectors = [
        ".message-content:last-child",
        ".chat-message:last-child",
        ".response-content",
        ".markdown-content"
    ]
    
    response_element = None
    for selector in response_selectors:
        response_element = await page.query_selector(selector)
        if response_element:
            break
    
    if response_element:
        return await response_element.inner_text()
    return ""

def count_brand_mentions(text, brands):
    """Count how many times each brand is mentioned in the text"""
    counts = defaultdict(int)
    text_lower = text.lower()
    for brand in brands:
        counts[brand] = text_lower.count(brand.lower())
    return dict(counts)

async def scrape_deepseek():
    """Main function to scrape DeepSeek responses"""
    if not EMAIL or not PASSWORD:
        raise ValueError("Please set DEEPSEEK_EMAIL and DEEPSEEK_PASSWORD in your .env file")
    
    results = []
    
    playwright, browser, context = await setup_stealth_browser()
    page = await context.new_page()
    
    try:
        # Login to DeepSeek
        print("Attempting to login to DeepSeek...")
        await login_to_deepseek(page)
        print("Login successful")
        
        # Navigate to chat interface if not already there
        if "chat" not in page.url.lower():
            await page.goto(DEEPSEEK_URL + "/chat", wait_until="networkidle")
        
        await page.wait_for_timeout(2000)  # Small delay after login
        
        for prompt in PROMPTS:
            print(f"Processing prompt: {prompt}")
            try:
                response = await send_prompt_and_get_response(page, prompt)
                counts = count_brand_mentions(response, BRANDS)
                
                result = {
                    "prompt": prompt,
                    "response": response,
                    "brand_mentions": counts,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(result)
                
                # Random delay between prompts
                delay = random.randint(3000, 7000)
                print(f"Waiting {delay//1000} seconds before next prompt...")
                await page.wait_for_timeout(delay)
            
            except Exception as e:
                print(f"Error processing prompt '{prompt}': {str(e)}")
                continue
        
        # Save results
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Fatal error occurred: {str(e)}")
    finally:
        await browser.close()
        await playwright.stop()
    
    return results

if __name__ == "__main__":
    asyncio.run(scrape_deepseek())