import feedparser
import openai
import requests
import json
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

# এনভায়রনমেন্ট থেকে OpenAI API Key নেওয়া (গিটহাবে সিকিউর থাকবে)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def fetch_and_process_rss(rss_url):
    print(f"Fetching news from: {rss_url}")
    feed = feedparser.parse(rss_url)
    
    for entry in feed.entries[:1]:
        original_title = entry.title
        original_summary = entry.get("summary", "")
        
        print(f"Original Title: {original_title}")
        
        # এআই দিয়ে বাংলায় রি-রাইট করা
        rewritten_data = rewrite_news_with_ai(original_title, original_summary)
        
        if rewritten_data:
            new_title = rewritten_data["rewritten_title"]
            print(f"AI Rewritten Title: {new_title}")
            
            # ফটোকার্ড জেনারেট করা
            generate_news_photocard(
                news_title=new_title,
                logo_path="client_logo.png",
                bg_template_path="template_bg.png",
                output_path="generated_photocard.png"
            )
            print("--- Photocard Generated Successfully! ---")

def rewrite_news_with_ai(original_title, original_summary):
    prompt = f"""
    You are a professional senior journalist. Rewrite this news in fluent, engaging Bengali:
    Original Title: {original_title}
    Original Summary: {original_summary}

    Provide output strictly in this JSON format:
    {{
        "rewritten_title": "নতুন বাংলা শিরোনাম",
        "rewritten_content": "রি-রাইট করা বাংলা নিউজ বিবরণ"
    }}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def generate_news_photocard(news_title, logo_path, bg_template_path, output_path="output_photocard.png"):
    try:
        base_img = Image.open(bg_template_path).convert("RGBA")
    except FileNotFoundError:
        base_img = Image.new("RGBA", (1200, 630), (15, 23, 42, 255))
        
    draw = ImageDraw.Draw(base_img)
    try:
        title_font = ImageFont.truetype("Kalpurush.ttf", 50)
    except IOError:
        title_font = ImageFont.load_default()

    wrapped_text = textwrap.fill(news_title, width=32)
    draw.text((103, 203), wrapped_text, fill="black", font=title_font)
    draw.text((100, 200), wrapped_text, fill="white", font=title_font)
    
    try:
        logo = Image.open(logo_path).convert("RGBA")
        logo_width = 200
        w_percent = (logo_width / float(logo.size[0]))
        logo_height = int(float(logo.size[1]) * float(w_percent))
        logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
        base_img.paste(logo, (950, 50), logo)
    except Exception as e:
        print(f"Logo skipped: {e}")

    base_img.convert("RGB").save(output_path, "PNG")

if __name__ == "__main__":
    sample_rss = "https://feeds.bbci.co.uk/bengali/rss.xml"
    fetch_and_process_rss(sample_rss)
    import json

# ধরা যাক, আপনার পাইথন স্ক্রিপ্ট বা OpenAI থেকে রি-রাইট করা নিউজগুলো একটি লিস্টে (List) রাখা আছে, 
# যার নাম দেওয়া হলো `scraped_news` (আপনার ভেরিয়েবলের নাম আলাদা হলে সেটি এখানে বসিয়ে দেবেন)।
# ফরম্যাটটি ঠিক নিচের মতো হতে হবে:

scraped_news = [
    {
        "title": "আপনার পাইথন স্ক্রিপ্ট দিয়ে আনা নিউজের শিরোনাম",
        "category": "প্রযুক্তি",
        "description": "নিউজের বিস্তারিত বা সারসংক্ষেপ...",
        "date": "আজ, ১০ মিনিট আগে",
        "image": "ইমেলের বা নিউজের ছবির ডিরেক্ট লিংক (URL)"
    }
]

# এবার এই কোডটুকু দিলেই পাইথন অটোমেটিক `news.json` ফাইল তৈরি করে ডাটাগুলো সেভ করে ফেলবে:
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(scraped_news, f, ensure_ascii=False, indent=4)

print("News successfully saved to news.json!")
