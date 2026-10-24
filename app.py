import os
import re
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import io
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline
import torch
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = "24earlynews_ai_image_transform_2026"

DATA_FILE = "articles_store.json"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- AI Image Generation Setup (Stable Diffusion) ---
# This requires a GPU. If you don't have one, use a CPU-optimized model or an API service.
# For demonstration, we use a placeholder function. Replace with actual pipeline for production.
# A real implementation would be:
# device = "cuda" if torch.cuda.is_available() else "cpu"
# model_id = "stabilityai/stable-diffusion-2-1"
# try:
#     pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_id, torch_dtype=torch.float16).to(device)
# except:
#     pipe = None # Or load a CPU model

def generate_transformed_image(input_image_path):
    """
    Analyzes the input image and generates a new, stylistically similar but unique image.
    This is a placeholder for a real AI generation pipeline (e.g., Stable Diffusion Img2Img).
    """
    try:
        # --- REAL AI IMPLEMENTATION PLACEHOLDER ---
        # In a real scenario, you'd load the image, generate a new one based on its style/prompt,
        # and save the output.

        # For now, we will just simulate by compressing and watermarking the image,
        # but this does NOT create a new copyright-safe image.
        # A real implementation would look like this:

        # if pipe is None: return input_image_path # Fallback
        # init_image = Image.open(input_image_path).convert("RGB").resize((512, 512))
        # prompt = "A photojournalistic image inspired by this composition"
        # images = pipe(prompt=prompt, image=init_image, strength=0.8, guidance_scale=7.5).images
        # transformed_path = input_image_path.replace(".jpg", "_ai.jpg")
        # images[0].save(transformed_path)
        # return transformed_path

        # --- SIMULATION (Compress & Rename for uniqueness) ---
        # We just rename and re-save to simulate a new file.
        # A true AI solution requires a dedicated GPU server.

        base_name = os.path.basename(input_image_path)
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}_ai_{int(datetime.now().timestamp())}{ext}"
        new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
        
        img = Image.open(input_image_path)
        img.save(new_path, optimize=True, quality=85) # Save with compression to create a distinct file
        
        # Add a subtle watermark to indicate it's generated
        watermark_text = "© 2026 24 EARLY NEWS - AI GENERATED"
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        # font = ImageFont.load_default() # Use a real font for production
        draw.text((10, 10), watermark_text, fill=(255, 255, 255, 128))
        img.save(new_path)

        return new_path

    except Exception as e:
        print(f"AI Generation Error: {str(e)}")
        return input_image_path # Fallback to original if AI fails

def get_articles():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                items = json.load(f)
                if isinstance(items, list) and len(items) > 10:
                    return items
        except Exception:
            pass
    return []

@app.route('/')
def home():
    try:
        articles = get_articles()
        return render_template('index.html', news=articles, news_list=articles)
    except Exception as e:
        return f"CRITICAL RENDER ERROR: {str(e)}", 500

@app.route('/news/<article_id>')
def view_article(article_id):
    try:
        articles = get_articles()
        target = next((item for item in articles if str(item.get('id')) == str(article_id)), articles[0])
        return render_template('single.html', article=target)
    except Exception:
        return redirect(url_for('home'))

@app.route('/submit-news', methods=['GET', 'POST'])
def submit_news():
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            category = request.form.get('category', 'India').strip()
            content = request.form.get('content', '').strip()
            
            if not title or not content:
                return redirect(url_for('submit_news'))

            # --- Handle Image (Upload or URL) ---
            final_img_path = 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1200' # Default
            
            # Option 1: Direct Upload
            if 'image_upload' in request.files and request.files['image_upload'].filename != '':
                file = request.files['image_upload']
                filename = secure_filename(file.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(upload_path)
                
                # Run the AI transformation on the uploaded file
                final_img_path = generate_transformed_image(upload_path)
                # Use the absolute URL for the AI image
                final_img_path = url_for('static', filename=f"uploads/{os.path.basename(final_img_path)}", _external=True)

            # Option 2: Online Image URL
            elif request.form.get('image_url', '').strip():
                img_url = request.form.get('image_url', '').strip()
                try:
                    # Download the image first
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        # Save the downloaded image locally
                        original_filename = "downloaded_" + secure_filename(os.path.basename(img_url)) or "image.jpg"
                        local_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
                        with open(local_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Run the AI transformation on the downloaded file
                        final_img_path = generate_transformed_image(local_path)
                        # Use the absolute URL for the AI image
                        final_img_path = url_for('static', filename=f"uploads/{os.path.basename(final_img_path)}", _external=True)

                    else:
                        final_img_path = img_url # Keep original URL if download fails
                except Exception as e:
                    print(f"URL Download Error: {str(e)}")
                    final_img_path = img_url # Keep original URL

            new_id = str(int(datetime.now().timestamp() * 1000))
            new_article = {
                'id': new_id,
                'title': title,
                'summary': content,
                'category': category,
                'link': f"/news/{new_id}",
                'image': final_img_path,
                'published': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            }

            all_news = get_articles()
            all_news.insert(0, new_article)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(all_news[:5000], f, ensure_ascii=False, indent=2)

            return redirect(f"/news/{new_id}")
        except Exception as e:
            return f"Submission Error: {str(e)}", 500

    return render_template('submit.html')

@app.route('/privacy')
def privacy_page(): return render_template('privacy.html')

@app.route('/about')
def about_page(): return render_template('about.html')

@app.route('/contact')
def contact_page(): return render_template('contact.html')

@app.route('/terms')
def terms_page(): return render_template('terms.html')

@app.route('/ads.txt')
def serve_ads_txt(): return send_from_directory('static', 'ads.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
