import streamlit as st
import subprocess
from ollama import chat, ResponseError
import os
import json
from datetime import datetime
import re
from PIL import Image
from modules.imagegen import generate_image  
import easygui
# File to store conversations

CONVERSATIONS_FILE = "conversations.json"

# Model Descriptions: Only models with <= 7B parameters
MODEL_DESCRIPTIONS = {
    "orca-mini": "A small, efficient model optimized for conversational tasks and responses.",
    "smollm": "A lightweight language model designed for minimal memory usage.",
    "smollm2": "An improved version of smollm with better accuracy and efficiency.",
    "tinydolphin": "A compact and fast model, ideal for small-scale conversations and code generation.",
    "dolphin-phi": "A model optimized for simple reasoning and code-based tasks.",
    "mistral-small": "A small variant of Mistral with high efficiency for quick and clean text output.",
    "stablelm2": "An optimized StableLM model for smooth and stable performance on conversational tasks.",
    "stable-code": "A model optimized for and understanding code snippets.",
    "wizard-vicuna-uncensored": "A conversational model focused on uncensored, creative output.",
    "openchat": "OpenChat is ideal for dynamic, multi-turn conversations with quick responses.",
    "aya:8b": "A fast and lightweight model with creative generation and comprehension capabilities.",
    "codeqwen": "CodeQwen is specifically designed for coding tasks and technical problem-solving.",
    "qwen2-math:7b": "Optimized for math and technical conversations, with accurate problem-solving skills.",
    "deepseek-llm:7b": "A general-purpose conversational model for small tasks and clear responses.",
    "neural-chat": "A lightweight chat model fine-tuned for human-like responses and small tasks.",
    "nous-hermes:7b": "A conversational assistant optimized for quick and accurate language outputs."
}

def load_conversations():
    """Load conversations from a JSON file."""
    if os.path.exists(CONVERSATIONS_FILE):
        with open(CONVERSATIONS_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}


def save_conversations():
    """Save current conversations to a JSON file."""
    with open(CONVERSATIONS_FILE, "w") as file:
        json.dump(st.session_state['conversations'], file, indent=4)


def is_model_installed(model_name):
    """Checks if a model is installed locally."""
    try:
        installed_models = subprocess.check_output(["ollama", "list"], universal_newlines=True)
        return model_name in installed_models
    except subprocess.CalledProcessError:
        return False


def install_model_with_progress(model_name):
    """Installs a model with progress tracking."""
    st.info(f"Installing model '{model_name}'. Please wait...")
    progress_bar = st.progress(0)

    process = subprocess.Popen(
        ["ollama", "pull", model_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8"
    )

    for line in process.stdout:
        line = line.strip()
        st.write(line)
        match = re.search(r'(\d+)%', line)
        if match:
            progress = int(match.group(1))
            progress_bar.progress(progress / 100)

    process.wait()
    if process.returncode == 0:
        st.success(f"Model '{model_name}' successfully installed!")
    else:
        st.error(f"Failed to install model '{model_name}'. Please try again.")


def generate_response_with_streaming(user_input, model, messages, placeholder):
    """Generates streaming AI response considering full conversation history."""
    # Check if the model is installed
    if not is_model_installed(model):
        install_model_with_progress(model)

    # Append the system prompt to the conversation
    system_prompt = st.session_state['system_prompt']
    full_conversation = f"System: {system_prompt}\n" + "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    
    prompt = f"Conversation so far:\n{full_conversation}\n\nNew input: {user_input}"
    
    try:
        response = chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        )
    except ResponseError as e:
        st.error(f"Model '{model}' not found. Please install it first.")
        return "Error: Model not found."

    full_response = ""
    for chunk in response:
        if 'message' in chunk and 'content' in chunk['message']:
            text = chunk['message']['content']
            full_response += text
            placeholder.markdown(full_response + "▌")
    placeholder.markdown(full_response)
    return full_response


def generate_conversation_title(messages, model):
    """Generates a title for the conversation based on the initial exchange."""
    prompt = "Summarize this conversation in 3-8 words for use as a title:\n\n"
    conversation_text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    response = chat(model=model, messages=[{'role': 'user', 'content': prompt + conversation_text}], stream=False)
    return response['message']['content'].strip()


def main():
    st.set_page_config(layout="wide", page_title="RYFAI Chat Interface")
    st.title("💬 RYFAI Chat Interface")

    # Add custom CSS for styling
    st.markdown(
        """
        <style>
        img {
            max-width: 100%;
            width: 400px; /* Set a fixed width for images */
            height: auto;
            margin: 0 auto;
            display: block;
        }
        .model-display {
            position: fixed;
            top: 10px;
            left: 10px;
            background-color: #f1f1f1;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Load conversations if not already in session_state
    if 'conversations' not in st.session_state:
        st.session_state['conversations'] = load_conversations()

    if 'current_conversation' not in st.session_state:
        st.session_state['current_conversation'] = None

    if 'system_prompt' not in st.session_state:
        st.session_state['system_prompt'] = "You are a helpful and friendly AI assistant."

    # Sidebar for managing conversations and system prompt
    with st.sidebar:
        st.header("🗂️ Conversations")
        conversation_titles = list(st.session_state['conversations'].keys())

        # Dropdown to select or start a conversation
        selected_conversation = st.selectbox(
            "Select a Conversation",
            ["New Conversation"] + conversation_titles,
            index=0 if not st.session_state['current_conversation'] else conversation_titles.index(st.session_state['current_conversation']) + 1
        )
        if selected_conversation == "New Conversation":
            start_new_conversation()
        else:
            st.session_state['current_conversation'] = selected_conversation

        # Model selection
        st.subheader("🧠 Model Selection")
        model_options = list(MODEL_DESCRIPTIONS.keys())
        selected_model = st.selectbox("Choose a model", model_options)

        # Display model description
        st.markdown(f"**Model Description:** {MODEL_DESCRIPTIONS.get(selected_model, 'No description available')}")

        # Update model for the current conversation
        if st.session_state['current_conversation']:
            st.session_state['conversations'][st.session_state['current_conversation']]['model'] = selected_model
            save_conversations()

        # System prompt input
        st.subheader("📝 System Prompt")
        st.session_state['system_prompt'] = st.text_area(
            "Edit the system prompt to control AI behavior:",
            value=st.session_state['system_prompt'],
            height=150
        )
        if st.button("Donate to the Dev!"):
            easygui.msgbox("Thank you so much for donating to RYFAI! It keeps projects like RYFAI alive!. The developer currently accepts Bitcoin, Monero, and Litecoin donations!\n\n"
            "Bitcoin: bc1qjnrvt3d8ms69zusvh244v5h2hya9yhqzsemtc2\n"
            "Litecoin: LRJRFiUWkQ1ZL1ZDDnaZ4D2VwtjxMtCe2E\n"
            "Monero: 494oHEbuekCRA8hcWyo81DLPsvy435neSdxJ33m9c4hf5UtJUARrq6f2vU3APWDosFW147pHDv2WK4fVWnWcemHK4d4Ene4"
            )

    # Display current model in the top left
    current_model = selected_model if st.session_state['current_conversation'] else "No model selected"
    st.markdown(
        f'<div class="model-display">Model: {current_model}</div>',
        unsafe_allow_html=True,
    )
    
    # Main Chat Interface
    if st.session_state['current_conversation']:
        display_chat_ui()
    else:
        st.info("Start a new conversation or select one from the sidebar.")



def display_chat_ui():
    """Displays a ChatGPT-like chat interface."""
    conversation = st.session_state['conversations'][st.session_state['current_conversation']]
    messages = conversation['messages']
    model = conversation.get('model', 'No model selected')

    # Display existing messages
    for msg in messages:
        with st.chat_message("user" if msg['role'] == 'user' else "assistant"):
            st.markdown(msg['content'])

    # Chat Input
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # Append user message
        messages.append({'role': 'user', 'content': user_input})
        save_conversations()
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate AI Response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = generate_response_with_streaming(user_input, model, messages, response_placeholder)
            response_placeholder.markdown(full_response)  # Display the response in the placeholder
            messages.append({'role': 'assistant', 'content': full_response})
            save_conversations()

            # Auto-generate title after the first user input
            if len(messages) == 2:  # First user input and AI response
                conversation_title = generate_conversation_title(messages, model)
                st.session_state['conversations'][conversation_title] = st.session_state['conversations'].pop(st.session_state['current_conversation'])
                st.session_state['current_conversation'] = conversation_title
                save_conversations()

        # Image generation option
        if "image" in user_input.lower() or "picture" in user_input.lower():
            st.info("**If the image generation model is not downloaded yet, this process will take a while**")
            st.info("Generating image...")
            try:
                image_path = generate_image(user_input)
                if image_path:
                    st.image(image_path, caption="Generated Image", width=400)  # Set a fixed width
                else:
                    st.error("Image generation failed. Please try again.")
            except Exception as e:
                st.error(f"Error generating image: {e}")


def start_new_conversation():
    """Creates a new conversation."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    default_title = f"New Conversation {timestamp}"
    st.session_state['conversations'][default_title] = {'model': None, 'messages': []}
    st.session_state['current_conversation'] = default_title
    save_conversations()

if __name__ == "__main__":
    main()
