import json
import re
import time
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from src.state import GraphState, EmailSummary
from src.config import settings

def clean_and_truncate(text: str, max_chars: int = 4000) -> str:
    return text[:max_chars]

def get_model():
    if settings.MODEL_PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0,
            convert_system_message_to_human=True 
        )
    elif settings.MODEL_PROVIDER == "groq":
        return ChatGroq(
            model_name=settings.MODEL_NAME,
            api_key=settings.GROQ_API_KEY,
            temperature=0
        )
    else:
        raise ValueError(f"Unknown model provider: {settings.MODEL_PROVIDER}")

def parse_json_from_response(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if json_match:
        text = json_match.group(1)
    
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json.loads(json_match.group())
    
    raise ValueError("No valid JSON found in response")

def analyze_with_retry(chain, email, max_retries: int = 3) -> dict:
    """Analyze email with retry logic."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            truncated_body = clean_and_truncate(email.body)
            response = chain.invoke({
                "subject": email.subject,
                "sender": email.sender,
                "body": truncated_body
            })
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            return parse_json_from_response(response_text)
            
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * settings.API_DELAY_SECONDS
                print(f"  ⏳ Retry {attempt + 1}/{max_retries} in {wait_time}s...")
                time.sleep(wait_time)
    
    raise last_error

def analyze_emails(state: GraphState) -> GraphState:
    if state.error:
        return state

    try:
        llm = get_model()
        results = []
        
        # Valid categories for fallback validation
        valid_categories = ["Marketing", "Job Updates", "Careers", "Finance", "Social", "System", "Other"]
        
        total = len(state.raw_emails)
        
        for idx, email in enumerate(state.raw_emails):
            if not email.body.strip():
                print(f"  ⏭️ Skipping empty email: {email.subject[:30]}...")
                continue
            
            # Rate limiting delay
            if idx > 0:
                time.sleep(settings.API_DELAY_SECONDS)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert email analyzer. Analyze the email and return a JSON object with these fields:
- summary_points: array of 2-4 key bullet points (strings, concise)
- category: one of Marketing, Job Updates, Careers, Finance, Social, System, Other
- importance: integer from 1 to 5 (5 = urgent/critical)

Return ONLY the JSON object, no other text."""),
                ("user", """Subject: {subject}
Sender: {sender}
Content:
{body}""")
            ])
            
            chain = prompt | llm
            
            try:
                print(f"  [{idx+1}/{total}] Analyzing: {email.subject[:40]}...")
                parsed = analyze_with_retry(chain, email, settings.MAX_RETRIES)
                
                category = parsed.get("category", "Other")
                if category not in valid_categories:
                    category = "Other"
                
                # Create EmailSummary object
                summary = EmailSummary(
                    id=email.id,
                    subject=email.subject,
                    sender=email.sender,
                    summary_points=parsed.get("summary_points", [])[:4],  # Limit to 4 points
                    category=category,
                    importance=int(parsed.get("importance", 3))
                )
                results.append(summary)
                print(f"  ✅ Done: {category} | Importance: {summary.importance}/5")
                
            except Exception as e:
                print(f"  ❌ Failed: {email.subject[:30]}... - {e}")
                continue

        print(f"\n📊 Analyzed {len(results)}/{total} emails successfully.")
        state.analyzed_emails = results
        return state
        
    except Exception as e:
        state.error = f"Error in analysis phase: {str(e)}"
        return state
