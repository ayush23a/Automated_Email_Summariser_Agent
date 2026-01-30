import base64
from email.message import EmailMessage
from src.state import GraphState
from src.tools.gmail import get_gmail_service

def create_draft(state: GraphState) -> GraphState:
    if state.error:
        print(f"Skipping draft creation due to error: {state.error}")
        return state

    if not state.analyzed_emails:
        print("No emails were analyzed. Skipping draft creation.")
        return state

    try:
        service = get_gmail_service()
        
        message = EmailMessage()
        message.set_content(state.final_digest)
        # For drafts, we don't need To/From headers
        # The user will fill them in when composing
        message["Subject"] = "Yesterday's Email Summary 📧"
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {
            "message": {
                "raw": encoded_message
            }
        }
        
        draft = service.users().drafts().create(userId="me", body=create_message).execute()
        
        print(f"✅ Draft created with ID: {draft['id']}")
        return state
        
    except Exception as e:
        state.error = f"Error creating draft: {str(e)}"
        return state
