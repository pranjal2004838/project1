from ai.gemini_client import call_gemini
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    print("[*] Testing Gemini API Connection...")
    if not os.getenv("GEMINI_API_KEY"):
        print("[-] GEMINI_API_KEY not found in .env")
        return

    prompt = "Return a JSON object with a 'status' field saying 'ok'."
    result = call_gemini(prompt)
    if result.get("status") == "ok":
        print("[+] Gemini API is working correctly!")
        print(f"    Response: {result}")
    else:
        print(f"[-] Gemini API test failed or returned unexpected JSON: {result}")

if __name__ == "__main__":
    test_gemini()
