import os
from dotenv import load_dotenv; load_dotenv()
import requests
import time

def _get_token():
    """Read Telegram bot token at runtime (after .env is loaded)."""
    return os.getenv("TELEGRAM_BOT_TOKEN", "")

def _get_chat_id():
    """Read Telegram chat ID at runtime (after .env is loaded)."""
    return os.getenv("TELEGRAM_CHAT_ID", "")

def send_approval_request(step_num, total_steps, action, params, rationale, risk_level):
    """Send approval request to Telegram and wait for response."""
    token = _get_token()
    chat_id = _get_chat_id()
    
    if not token or not chat_id:
        print("⚠️  Telegram not configured. Falling back to terminal approval.")
        return None
    
    message = f"""🤖 *AGENT NEEDS APPROVAL*

*Step {step_num}/{total_steps}*
*Action:* `{action}`
*Risk:* {risk_level}

*Rationale:*
{rationale}

*Params:*
```{params}```

Reply with:
✅ *APPROVE* — to proceed
❌ *REJECT* — to cancel
⏱️ You have 10 minutes to respond.
"""
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"📱 Sent approval request to Telegram (Step {step_num})")
            return True
        else:
            print(f"⚠️  Telegram send failed: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️  Telegram error: {e}")
        return None

def check_telegram_response(timeout_seconds=600):
    """Poll Telegram for user response. Returns 'approve', 'reject', or None."""
    token = _get_token()
    chat_id = _get_chat_id()
    
    if not token or not chat_id:
        return None
    
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    start_time = time.time()
    last_update_id = None
    
    while time.time() - start_time < timeout_seconds:
        try:
            params = {"offset": last_update_id + 1} if last_update_id else {}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("ok") and data.get("result"):
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    message = update.get("message", {})
                    text = message.get("text", "").lower().strip()
                    msg_chat_id = message.get("chat", {}).get("id")
                    
                    if str(msg_chat_id) == str(chat_id):
                        if text in ["approve", "yes", "y", "✅", "go", "ok"]:
                            send_confirmation("✅ Step APPROVED. Agent is proceeding...")
                            return "approve"
                        elif text in ["reject", "no", "n", "❌", "stop", "cancel"]:
                            send_confirmation("❌ Step REJECTED. Agent stopped.")
                            return "reject"
            
            time.sleep(3)
        except Exception as e:
            print(f"⚠️  Polling error: {e}")
            time.sleep(5)
    
    print("⏱️  No response from Telegram. Falling back to terminal.")
    return None

def send_confirmation(message_text):
    """Send a confirmation message back to Telegram."""
    token = _get_token()
    chat_id = _get_chat_id()
    
    if not token or not chat_id:
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def send_status_update(message_text):
    """Send general status updates to Telegram."""
    token = _get_token()
    chat_id = _get_chat_id()
    
    if not token or not chat_id:
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass
