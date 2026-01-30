from datetime import datetime, timedelta
import pytz
import base64
import re
from html.parser import HTMLParser
from src.state import GraphState, EmailItem
from src.tools.gmail import get_gmail_service
from src.config import settings

# Try to import BeautifulSoup, fallback to basic HTML stripping
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

def clean_body(text: str) -> str:
    """Simple cleanup to remove excess whitespace"""
    return " ".join(text.split())

def extract_sender_name(sender: str) -> str:
    """Extract just the name from 'Name <email>' format"""
    if '<' in sender:
        return sender.split('<')[0].strip().strip('"')
    return sender

def strip_html_basic(html: str) -> str:
    """Basic HTML stripping without BeautifulSoup"""
    # Remove script and style elements
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    html = re.sub(r'<[^>]+>', ' ', html)
    # Decode common HTML entities
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return html

def html_to_text(html: str) -> str:
    """Convert HTML to plain text"""
    if HAS_BS4:
        soup = BeautifulSoup(html, 'lxml')
        # Remove script and style elements
        for element in soup(['script', 'style', 'head', 'meta', 'link']):
            element.decompose()
        text = soup.get_text(separator=' ')
    else:
        text = strip_html_basic(html)
    
    return clean_body(text)

def extract_body_from_parts(parts: list, prefer_plain: bool = True) -> str:
    """Recursively extract body from email parts, handling nested multipart"""
    plain_text = ""
    html_text = ""
    
    for part in parts:
        mime_type = part.get("mimeType", "")
        
        # Handle nested multipart
        if "parts" in part:
            nested_body = extract_body_from_parts(part["parts"], prefer_plain)
            if nested_body:
                return nested_body
        
        data = part.get("body", {}).get("data")
        if not data:
            continue
            
        try:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        except Exception:
            continue
        
        if mime_type == "text/plain":
            plain_text += decoded
        elif mime_type == "text/html":
            html_text += decoded
    
    # Prefer plain text if available, otherwise convert HTML
    if plain_text.strip():
        return plain_text
    elif html_text.strip():
        return html_to_text(html_text)
    
    return ""

def fetch_emails(state: GraphState) -> GraphState:
    try:
        service = get_gmail_service()
        
        ist = pytz.timezone(settings.TIMEZONE)
        now = datetime.now(ist)
        today = now.date()
        yesterday = today - timedelta(days=1)
        
        # Format dates for Gmail query (YYYY/MM/DD)
        after_str = yesterday.strftime("%Y/%m/%d")
        before_str = today.strftime("%Y/%m/%d")
        
        query = f"after:{after_str} before:{before_str}"
        print(f"📬 Fetching emails with query: {query}")
        
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        
        # Apply email fetch limit (0 = no limit)
        total_available = len(messages)
        if settings.MAX_EMAILS_TO_FETCH > 0 and total_available > settings.MAX_EMAILS_TO_FETCH:
            print(f"⚠️ Found {total_available} emails, limiting to {settings.MAX_EMAILS_TO_FETCH}")
            messages = messages[:settings.MAX_EMAILS_TO_FETCH]
        
        email_items = []
        for msg in messages:
            try:
                msg_detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
                payload = msg_detail.get("payload", {})
                headers = payload.get("headers", [])
                
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown)")
                date_str = next((h["value"] for h in headers if h["name"] == "Date"), "")
                
                # Extract body with HTML fallback
                body = ""
                if "parts" in payload:
                    body = extract_body_from_parts(payload["parts"])
                else:
                    # Single part email
                    mime_type = payload.get("mimeType", "")
                    data = payload.get("body", {}).get("data")
                    if data:
                        try:
                            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            if mime_type == "text/html":
                                body = html_to_text(decoded)
                            else:
                                body = decoded
                        except Exception:
                            pass
                
                email_items.append(
                    EmailItem(
                        id=msg["id"],
                        subject=subject,
                        sender=extract_sender_name(sender),
                        body=clean_body(body),
                        received_at=date_str
                    )
                )
            except Exception as e:
                print(f"⚠️ Failed to fetch email {msg['id']}: {e}")
                continue
            
        print(f"✅ Fetched {len(email_items)}/{total_available} emails.")
        state.raw_emails = email_items
        return state

    except Exception as e:
        state.error = f"Error fetching emails: {str(e)}"
        return state
