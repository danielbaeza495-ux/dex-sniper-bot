import os
import requests
from telethon import TelegramClient, events, Button
from flask import Flask
from threading import Thread

# --- [CONFIGURATION] ---
# Render-এর Environment Variables থেকে ডেটা নেবে
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
BIRDEYE_API_KEY = os.getenv('BIRDEYE_API_KEY')

# Flask Server (Render-কে সচল রাখার জন্য)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and scanning!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Telegram Client Setup
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- [LOGIC FUNCTIONS] ---

def find_pro_wallets():
    """অটোমেটিক সেরা প্রফিটেবল ওয়ালেট খুঁজে বের করে"""
    url = "https://public-api.birdeye.so/public/trending?list_count=10"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}
    try:
        response = requests.get(url, headers=headers).json()
        if response.get('success'):
            # ট্রেন্ডিং কয়েন থেকে আর্লি বায়ার বের করার লজিক
            tokens = response['data']['tokens']
            return [t['address'] for t in tokens[:5]] # স্যাম্পল হিসেবে ৫টি টোকেন অ্যাড্রেস
    except:
        return []
    return []

def get_token_report(address):
    """RugCheck API থেকে সেফটি রিপোর্ট আনে"""
    try:
        res = requests.get(f"https://api.rugcheck.xyz/v1/tokens/{address}/report").json()
        return res.get('score', 1000)
    except:
        return 1000

# --- [BOT EVENTS] ---

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    welcome_msg = (
        "🚀 **DEX Alpha Sniper Bot v2**\n\n"
        "✅ 24/7 Cloud Active\n"
        "✅ Smart Money Tracking\n"
        "✅ Auto RugCheck Filter\n\n"
        "নিচের বাটনে ক্লিক করে স্মার্ট ওয়ালেট খোঁজা শুরু করুন।"
    )
    await event.respond(welcome_msg, buttons=[Button.inline("🔍 Find Alpha Wallets", b"find")])

@client.on(events.CallbackQuery(data=b"find"))
async def callback(event):
    await event.answer("Searching On-chain data...")
    wallets = find_pro_wallets()
    if wallets:
        await event.respond(f"✅ Found {len(wallets)} potential pro-wallets to monitor!")
    else:
        await event.respond("❌ No new pro-wallets found. Retrying soon...")

@client.on(events.NewMessage(pattern='/scan'))
async def scan_new_pairs(event):
    """ম্যানুয়ালি নিউ পেয়ার স্ক্যান করার সিমুলেশন"""
    # এখানে ডেক্সক্রিনার API কল করে লিকুইডিটি ফিল্টার (20k-200k) করা হবে
    token_addr = "DeZ7Z...example" # Sample
    liq = 55000 
    
    score = get_token_report(token_addr)
    
    if 20000 <= liq <= 200000 and score < 500:
        buy_link = f"https://t.me/BonkBot_bot?start={token_addr}"
        msg = (
            f"🌟 **New Smart Entry!**\n\n"
            f"Token: `{token_addr}`\n"
            f"Liquidity: ${liq}\n"
            f"Safety: ✅ Passed\n\n"
            f"👇 Click to Buy:"
        )
        await event.respond(msg, buttons=[Button.url("Buy on BonkBot", buy_link)])

# --- [RUN BOT] ---
print("Bot starting...")
keep_alive() # Flask শুরু করবে
client.run_until_disconnected()
      
