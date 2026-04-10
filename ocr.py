# social_media_analytics.py
# Works with: openai>=1.0.0

import os
import pandas as pd
from PIL import Image
import pytesseract
from openai import OpenAI

# -------------------------
# 0) OpenAI client (reads key from env)
# -------------------------
# Set your key once in your shell:
#   Windows (PowerShell):  $env:OPENAI_API_KEY="sk-...."
#   macOS/Linux:           export OPENAI_API_KEY="sk-...."
client = OpenAI(api_key="sk-xxxxx")  # picks up OPENAI_API_KEY from environment

# -------------------------
# 1) Dummy Data (text + image)
# -------------------------
posts = [
    {"type": "text", "content": "I love the new iPhone! #Apple #Awesome"},
    {"type": "text", "content": "Worst delivery experience ever. #Disappointed"},
    {"type": "image", "content": "meme.png"}  # Suppose meme.png has text
]

# -------------------------
# 2) OCR for images
# -------------------------
def extract_text_from_image(img_path: str) -> str:
    try:
        img = Image.open(img_path)
        text = pytesseract.image_to_string(img)
        text = (text or "").strip()
        return text if text else "(No readable text found in image)"
    except Exception as e:
        return f"(Error reading image: {e})"

# Convert image posts → text posts using OCR
for post in posts:
    if post.get("type") == "image":
        post["content"] = extract_text_from_image(post["content"])
        post["type"] = "text"

# -------------------------
# 3) Load into DataFrame
# -------------------------
df = pd.DataFrame(posts)
print("\n📊 Collected Posts:\n", df)

# -------------------------
# 4) LLM Analysis (OpenAI)
# -------------------------
def analyze_post(text: str) -> str:
    prompt = (
        "Analyze the following social media post and answer in JSON with keys: "
        "sentiment (Positive/Negative/Neutral), topics (list of keywords), "
        "sarcastic (Yes/No), and reason (1–2 sentences).\n\n"
        f"Post: {text}"
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise social-media insights analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"(LLM error: {e})"

df["analysis"] = df["content"].apply(analyze_post)

# -------------------------
# 5) GenAI Summary
# -------------------------
all_posts = "\n".join(df["content"].tolist())
summary_prompt = (
    "You are preparing a brief for a brand manager.\n"
    "Summarize the following social media discussions into:\n"
    "1) Key themes (bullets), 2) Overall sentiment, 3) Top risks, "
    "4) Quick recommendations (bullets).\n\n"
    f"{all_posts}"
)

try:
    summary = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.5,
    ).choices[0].message.content.strip()
except Exception as e:
    summary = f"(LLM error during summary: {e})"

print("\n📝 Insights Summary:\n", summary)
print("\n✅ Analysis column added. Preview:\n", df[["content", "analysis"]])