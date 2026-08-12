"""AI-powered extraction — describe what you want, get structured data."""
import os, json

def extract_with_ai(url: str, intent: str, **kwargs) -> list:
    """Fetch page and use AI to extract structured data based on intent."""
    from scrapetoolai import fetch
    page = fetch(url)
    text = page.get_text()[:4000] if hasattr(page, 'get_text') else str(page)[:4000]
    
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GOOGLE_AI_KEY")
    if not api_key:
        print("AI extraction requires OPENAI_API_KEY or GOOGLE_AI_KEY in environment.")
        print("Falling back to raw text extraction.")
        return [{"raw_text": text}]
    
    if os.environ.get("OPENAI_API_KEY"):
        return _extract_openai(text, intent)
    else:
        return _extract_gemini(text, intent)

def _extract_openai(text: str, intent: str) -> list:
    try:
        import openai
        client = openai.OpenAI()
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract structured data from web page text. Return JSON array."},
                {"role": "user", "content": f"From this page text, extract: {intent}\n\nPage text:\n{text}"}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content).get("items", [])
    except Exception as e:
        return [{"error": str(e)}]

def _extract_gemini(text: str, intent: str) -> list:
    try:
        import google.generativeai as genai
        import os
        genai.configure(api_key=os.environ["GOOGLE_AI_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(f"Extract as JSON array: {intent}\n\nFrom:\n{text}")
        return json.loads(resp.text)
    except Exception as e:
        return [{"error": str(e)}]
