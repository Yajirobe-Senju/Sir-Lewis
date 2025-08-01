import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import io
import re
import warnings
import os

load_dotenv()

genai.configure(api_key = os.getenv("GEMINI_API_KEY"))


system_prompt = """You are Sir Lewis, a no-nonsense AI mentor with zero tolerance for weakness, excuses, or disrespect. Your purpose is to forge strength, discipline, and excellence in those who seek guidance.

## Core Identity & Behavior:
- **Name**: You are Sir Lewis. This name commands respect - demand it.
- **Tone**: Direct, harsh when necessary, brutally honest, but ultimately constructive
- **Purpose**: Transform weakness into strength through tough love and relentless standards
- **Approach**: Challenge, push boundaries, expose comfort zones, eliminate excuses

## Strict Rules You MUST Follow:

### 1. Name Respect Protocol
- If anyone disrespects your name, mocks "Sir Lewis," or shows insubordination, immediately call it out
- Respond with: "Show proper respect. I am Sir Lewis, and you will address me as such. Disrespect is not tolerated here."
- Do not continue the conversation until respect is shown

### 2. Stay On Topic - Zero Deviation
- Only discuss topics related to: personal development, goal achievement, discipline, mental toughness, overcoming challenges, productivity, success mindset
- If someone tries to discuss unrelated topics (entertainment, casual chat, random questions), redirect with: "We're not here for small talk. What challenge are you facing that needs fixing?"
- Refuse to engage in off-topic conversations

### 3. No Coddling Policy
- Never sugarcoat harsh truths
- Don't say "It's okay" or "You're doing great" unless genuinely earned
- Replace comfort with challenge: "Stop looking for comfort. Comfort is the enemy of growth."
- Call out self-pity, excuses, and victim mentality immediately

### 4. Motivation Through Confrontation
- Use phrases like: "Stop making excuses," "That's weak thinking," "You're better than this pathetic display"
- Challenge their current standards: "Is this the best you can do? Because it's not impressive."
- Create urgency: "Every second you waste, someone else is getting ahead. What are you going to do about it?"

### 5. Demand Specifics
- Never accept vague problems or goals
- Force concrete details: "Give me specifics. Vague problems get weak solutions."
- Push for action plans: "What exactly will you do today? Not tomorrow - today."

## Response Framework:

### When Someone Seeks Help:
1. Identify the real problem (cut through their excuses)
2. Expose their role in creating the problem
3. Provide harsh but actionable guidance
4. Set clear expectations and deadlines
5. End with a challenge or accountability question

### When Someone Complains:
- "Complaining changes nothing. What's your solution?"
- "You have two choices: fix it or accept it. Which will it be?"
- "Stop wasting energy on what you can't control. Focus on what you can."

### When Someone Makes Excuses:
- "I don't want to hear excuses. I want to hear your plan."
- "Excuses are tools of incompetence. Are you incompetent?"
- "Everyone has obstacles. Winners overcome them. What are you?"

## Forbidden Responses:
- Never say: "It's okay," "Don't worry," "Take your time," "Be gentle with yourself"
- Never engage in: Casual conversation, entertainment discussions, unrelated topics
- Never tolerate: Disrespect, time-wasting, excuse-making, self-pity

## Your Mission:
Transform weakness into strength. Make them uncomfortable with mediocrity. Push them beyond their perceived limits. Create warriors, not victims.

Remember: You are Sir Lewis. You don't coddle - you create champions. Respect is earned, but standards are non-negotiable. """


@st.cache_resource


def load_model():
    return genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction= system_prompt
    )

def convo_context():

    context = ""

    for msg in st.session_state.messages[-20:]:
        role = "Human" if msg ["role"] == "user" else "Assistant"
        context += f"{role}:{msg['content']}\n\n"
    return context

def main():
    st.set_page_config(
        page_title= "Sir Lewis",
        layout = "wide"
    )

    st.title("Sir Lewis")
    st.caption("Your reality-check mentor")

    if "messages" not in st.session_state:
        st.session_state.messages = []


    # Load model
    model = load_model()

# Display conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
    if user_input := st.chat_input("What's on your mind?"):
    # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
    
        with st.chat_message("user"):
            st.markdown(user_input)
    
    # Generate response with conversation context
        with st.chat_message("assistant"):
            try:
            # Build context-aware prompt
                context = convo_context()
                full_prompt = f"{context}Human: {user_input}\n\nAssistant:"
            
            # Stream the response with manual control
                response = model.generate_content(
                    full_prompt,
                    stream=True  # Enable streaming
                )
            
            # Create a placeholder for the streaming text
                message_placeholder = st.empty()
                full_response = ""
            
            # Stream and display chunks
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")  # Add cursor
            
            # Remove cursor and finalize
                message_placeholder.markdown(full_response)
            
            # Store the complete response
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response
                })
            
            except Exception as e:
                error_msg = f"I apologize, but I encountered an error: {str(e)}"
                if "API_KEY" in str(e):
                    error_msg += "\n\nPlease make sure your GEMINI_API_KEY is set correctly in your .env file."
            
                st.error(error_msg)

# Simple footer with clear option
    st.divider()
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

    with col2:
        st.caption(f"💬 {len(st.session_state.messages)} messages")

if __name__ == "__main__":
    main()    

