# backend/chatbot_logic.py

def generate_reply(user_input: str) -> str:
    # Very basic placeholder logic
    if "hello" in user_input.lower():
        return "Hi there! How can I assist you today?"
    elif "image" in user_input.lower():
        return "Thanks for sending the image! I'll look at it soon."
    else:
        return "I'm still learning. Can you say that differently?"
