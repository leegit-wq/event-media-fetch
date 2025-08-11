import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BING_API_KEY = os.getenv("BING_API_KEY")
BING_API_ENDPOINT = os.getenv("BING_API_ENDPOINT")
SCREENSHOT_API_KEY = os.getenv("SCREENSHOT_API_KEY")

if not all([BING_API_KEY, BING_API_ENDPOINT, SCREENSHOT_API_KEY]):
    raise ValueError("❌ 缺少必要的 API Key，请检查 GitHub Secrets 设置。")

# 创建输出文件夹
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# 读取事件 JSON
with open("events_2024_corrected.json", "r", encoding="utf-8") as f:
    events = json.load(f)

# Bing 图片搜索
def bing_image_search(query):
    url = f"{BING_API_ENDPOINT}/images/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 3}
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    return [img["contentUrl"] for img in data.get("value", [])]

# 截取网页截图
def take_screenshot(url, filename):
    api_url = f"https://shot.screenshotapi.net/screenshot"
    params = {
        "token": SCREENSHOT_API_KEY,
        "url": url,
        "full_page": "true",
        "output": "image",
    }
    resp = requests.get(api_url, params=params)
    if resp.status_code == 200:
        with open(filename, "wb") as f:
            f.write(resp.content)

# 主流程
for event in events:
    title = event["title"]
    print(f"🔍 处理事件: {title}")

    # 1. 搜索图片
    images = bing_image_search(title)
    for idx, img_url in enumerate(images, start=1):
        try:
            img_data = requests.get(img_url, timeout=10).content
            img_path = output_dir / f"{title}_img{idx}.jpg"
            with open(img_path, "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"⚠️ 图片下载失败: {e}")

    # 2. 新闻截图
    if "link" in event and event["link"]:
        screenshot_path = output_dir / f"{title}_screenshot.png"
        try:
            take_screenshot(event["link"], screenshot_path)
        except Exception as e:
            print(f"⚠️ 截图失败: {e}")

print("✅ 全部处理完成！结果保存在 output/ 文件夹")
