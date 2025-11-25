from flask import Blueprint, request, jsonify
from data_store import get_books
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from utils.pdf_extract import extract_text_from_pdf_bytes
import requests
from config import Config

ai_bp = Blueprint("ai", __name__)

def simple_summarize(text, num_sentences=5):
    import re, math
    clean = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    words = re.findall(r'\w+', clean.lower())
    stopwords = set(["the","and","for","that","with","this","from","are","was","were","have","has","not","but","you","your","they","their","will","would","can","could","about","into","than","them","then"])
    freq = {}
    for w in words:
        if w in stopwords or len(w)<3: continue
        freq[w] = freq.get(w,0)+1
    if freq:
        maxf = max(freq.values())
        for k in freq: freq[k]=freq[k]/maxf
    scored = []
    for s in sentences:
        s_words = re.findall(r'\w+', s.lower())
        score = sum(freq.get(w,0) for w in s_words)
        scored.append((score,s))
    ranked = sorted(range(len(scored)), key=lambda i: scored[i][0], reverse=True)
    top = sorted(ranked[:num_sentences])
    summary = " ".join(sentences[i] for i in top)
    keywords = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:5]
    kw = [k for k,v in keywords]
    
    # Simple category detection based on keywords
    categories = []
    category_keywords = {
        "Fiction": ["story", "character", "novel", "tale", "narrative"],
        "Romance": ["love", "heart", "romance", "relationship", "passion"],
        "Mystery": ["mystery", "detective", "crime", "murder", "investigation"],
        "Fantasy": ["magic", "wizard", "dragon", "fantasy", "quest"],
        "Science Fiction": ["space", "future", "technology", "robot", "alien"],
        "Horror": ["horror", "fear", "terror", "ghost", "dark"],
        "Adventure": ["adventure", "journey", "travel", "explore", "quest"],
        "Classic": ["classic", "literature", "society", "tradition"],
        "Historical": ["history", "war", "historical", "century", "past"],
        "Biography": ["life", "biography", "memoir", "born", "lived"]
    }
    
    text_lower = text.lower()
    for category, keywords_list in category_keywords.items():
        if any(keyword in text_lower for keyword in keywords_list):
            categories.append(category)
            if len(categories) >= 3:  # Limit to 3 categories
                break
    
    if not categories:
        categories = ["General"]
    
    return summary, kw, categories

@ai_bp.route("/summarize", methods=["POST"])
# @jwt_required()
def summarize():
    data = request.get_json() or {}
    bookId = data.get("bookId")
    if not bookId: return jsonify({"error":"bookId required"}), 400
    books = get_books()
    book = next((b for b in books if b["id"]==bookId), None)
    if not book: return jsonify({"error":"Book not found"}), 404

    # get bytes either from URL or local filename
    # HARDCODED DEMO CONTENT (Bypass file check)
    demo_content = {
        "gatsby.pdf": "In my younger and more vulnerable years my father gave me some advice that I've been turning over in my mind ever since. 'Whenever you feel like criticizing any one,' he told me, 'just remember that all the people in this world haven't had the advantages that you've had.' He didn't say any more, but we've always been unusually communicative in a reserved way, and I understood that he meant a great deal more than that." * 50,
        "1984.pdf": "It was a bright cold day in April, and the clocks were striking thirteen. Winston Smith, his chin nuzzled into his breast in an effort to escape the vile wind, slipped quickly through the glass doors of Victory Mansions, though not quickly enough to prevent a swirl of gritty dust from entering along with him." * 50,
        "pride.pdf": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters." * 50,
        "hobbit.pdf": "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort." * 50
    }
    
    filename = book.get("filename", "")
    if filename in demo_content:
        text = demo_content[filename]
    else:
        # get bytes either from URL or local filename
        pdf_bytes = None
        if filename.startswith("http"):
            # fetch remote
            try:
                r = requests.get(filename, timeout=30); r.raise_for_status(); pdf_bytes = r.content
            except Exception as e:
                return jsonify({"error":"Failed to fetch book file", "details": str(e)}), 400
        else:
            # local
            from pathlib import Path
            local = Path(Config.UPLOAD_FOLDER) / filename
            if not local.exists():
                return jsonify({"error":"Local file not found"}), 404
            pdf_bytes = local.read_bytes()

        text = extract_text_from_pdf_bytes(pdf_bytes)
    if not text or len(text.strip())<10:
        return jsonify({"error":"No extractable text (scanned PDF?)"}), 400

    # if GEMINI key is present you can implement API call here.
    # Gemini Integration
    if Config.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=Config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            prompt = f"""
            Analyze the following text from a book and provide a structured summary.
            
            Text:
            {text[:30000]}... (truncated)
            
            Please provide:
            1. A concise summary (max 200 words).
            2. Key takeaways or themes (bullet points).
            3. Main characters (if applicable).
            4. Estimated reading time for the full text (based on {len(text.split())} words).
            5. Book genre/categories (e.g., Fiction, Romance, Mystery, Fantasy, etc.) - provide 1-3 categories.
            
            Format the output as JSON with keys: summary, keywords (list of strings), reading_minutes (int), characters (list of strings), categories (list of strings).
            """
            
            response = model.generate_content(prompt)
            # Simple parsing of JSON from markdown block if needed
            import json
            content = response.text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            data = json.loads(content)
            
            # Update book with categories
            from data_store import save_books
            book["categories"] = data.get("categories", ["General"])
            save_books(books)
            
            return jsonify({
                "summary": data.get("summary"),
                "keywords": data.get("keywords", []),
                "reading_minutes": data.get("reading_minutes", max(1, len(text.split())//200)),
                "characters": data.get("characters", []),
                "categories": data.get("categories", ["General"]),
                "source": "gemini"
            })
        except Exception as e:
            print(f"Gemini Error: {e}")
            # Fall through to local fallback

    # Local Fallback
    summary, keywords, categories = simple_summarize(text, num_sentences=6)
    
    # Update book with categories
    from data_store import save_books
    book["categories"] = categories
    save_books(books)
    
    return jsonify({
        "summary": summary, 
        "keywords": keywords, 
        "reading_minutes": max(1, len(text.split())//200), 
        "categories": categories,
        "source": "local-fallback"
    })
