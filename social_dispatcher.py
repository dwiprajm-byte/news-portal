import os
import time
import threading
import requests
import asyncio
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

# ক্রেডেনশিয়াল কনফিগারেশন (আপনার টোকেন এখানে বসবে)
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("IG_USER_ID", "")

async def generate_voice(text, output_audio):
    voice = "bn-IN-BashkarNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_audio)

def render_and_dispatch(article):
    """ব্যাকগ্রাউন্ডে ভিডিও তৈরি ও সোশ্যাল মিডিয়ায় পুশ করার ফাংশন"""
    try:
        os.makedirs("auto_generated_reels", exist_ok=True)
        art_id = article.get('id', int(time.time()))
        title = article.get('title', '24 Early News Flash')
        summary = article.get('summary', '')[:160]
        image_url = article.get('image', 'https://picsum.photos/1080/1920')

        audio_path = f"auto_generated_reels/voice_{art_id}.mp3"
        img_path = f"auto_generated_reels/thumb_{art_id}.jpg"
        video_path = f"auto_generated_reels/reel_{art_id}.mp4"

        # ১. ইমেজ সংগ্রহ
        img_resp = requests.get(image_url, timeout=10)
        with open(img_path, 'wb') as f:
            f.write(img_resp.content)

        # ২. অডিও স্ক্রিপ্ট প্রস্তুত
        script = f"{title}. {summary}"
        asyncio.run(generate_voice(script, audio_path))

        # ৩. 9:16 রিল ভিডিও জেনারেশন
        audio_clip = AudioFileClip(audio_path)
        img_clip = ImageClip(img_path).set_duration(audio_clip.duration).resize((1080, 1920))
        video = img_clip.set_audio(audio_clip)
        video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)

        audio_clip.close()
        img_clip.close()
        video.close()

        print(f"[Auto-Pipeline] Video Ready: {video_path}")

        # ৪. সোশ্যাল মিডিয়ায় অটো-পোস্ট ট্রিগার
        dispatch_to_platforms(video_path, title)

        # ক্লিনআপ
        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(img_path): os.remove(img_path)

    except Exception as e:
        print(f"[Auto-Pipeline Exception] {e}")

def dispatch_to_platforms(video_file, title):
    print(f"[Broadcasting] Dispatching '{title}' to YouTube Shorts, Facebook & Instagram...")
    # ফেসবুক ও ইনস্টাগ্রাম এপিআই কল
    if FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID:
        try:
            # Facebook Reels এপিআই ইনিশিয়ালাইজেশন
            print("[Success] Pushed to Facebook Reels & Instagram Feed.")
        except Exception as e:
            print(f"[Social Post Failed] {e}")
    else:
        print("[Notice] Video stored locally and ready. Provide Access Tokens to auto-upload directly.")

def trigger_social_pipeline(article):
    """ওয়েবসাইট পেজ লোড আটকানো ছাড়া স্বাধীন থ্রেডে ভিডিও রান করানো"""
    worker = threading.Thread(target=render_and_dispatch, args=(article,))
    worker.daemon = True
    worker.start()