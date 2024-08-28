import customtkinter as ctk
import easygui
from PIL import ImageGrab
import os
import webbrowser
import subprocess
import ollama

def main():
    root = ctk.CTk()
    root.geometry("700x570")
    root.title("RYFAI")
    root.resizable(False, False)  # Make the window unadjustable

    # Define model descriptions
    model_descriptions = {
        "phi": "An open source model trained by Microsoft Corporation. Trained on about 2 billion parameters\n"
               "Good performance-capability ratio",
        "phi3": "An enhanced version of phi. Good performance-capability ratio.",
        "mistral": "mistral is developed by French company Mistral AI. Medium performance-capability ratio on most laptops.",
        "llava": "Integrates both vision and language capabilities. Vision is not available on this app yet.\n"
                 "Trained on about 7 billion parameters. Poor performance-capability ratio on most laptops.",
        "llama2":"Developed by Meta AI, llama2 is open source and is used in many businesses like hospitals.\n"
                 "Medium performance-capability ratio on most laptops.",
        "llama2-uncensored": "Fine tuned from llama2, llama2-uncensored is uncensored and has no boundaries,\n"
                             "So it WILL be explicit and swear sometimes.",
        "orca-mini": "An extremely quantized version of Microsoft's OpenOrca. Very good performance-capability ratio",
        "tinyllama": "An extremely quantized version of Meta AI's llama2. Poor capability-performance ratio",
        "openchat": "The only model developed by Intel. Ok performance-capability ratio"
    }

    def is_model_installed(model_name):
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            installed_models = result.stdout.splitlines()
            return any(model_name in model for model in installed_models)
        except Exception as e:
            easygui.msgbox(f"Error checking installed models: {e}")
            return False

    def install_model(model_name):
        try:
            
            subprocess.run(['ollama', 'pull', model_name])
            easygui.msgbox(f"Model '{model_name}' installed successfully.")
        except Exception as e:
            easygui.msgbox(f"Error installing model '{model_name}': {e}")

    def show_model_description(selected_model):
        description = model_descriptions.get(selected_model, "No description available.")
        description_label.configure(text=description)
        model_label.configure(text=f"Current Model: {selected_model}")

        if not is_model_installed(selected_model):
            if easygui.ynbox(f"The model '{selected_model}' is not installed. Do you want to install it now?", 'Install Model', ('Yes', 'No')):
                install_model(selected_model)

    def howtouse():
        webbrowser.open("https://reclaimyourfreedomai.streamlit.app/")

    def about():
        easygui.msgbox("RYFAI is a completely private AI program that cares about it's users\n"
                       "It does not steal any user data and sell it to advertisers or use it to train\n"
                       "models. It is currently NOT open source as well as the RYFAI website, and all\n"
                       "models that are used by RYFAI are open-source or open-weights models.")

    def send():
        user_input = text_input.get("1.0", "end-1c").strip()
        if not user_input:
            easygui.msgbox("Please enter a question or prompt.")
            return
        
        selected_model = model_var.get()
        if selected_model == "Select a model":
            easygui.msgbox("Please select a model.")
            return

        # Clear the text input area
        text_input.delete("1.0", "end")

        # Display the user's input in the chat area
        text_area.configure(state="normal")
        text_area.insert("end", f"User: {user_input}\n")
        
        # Get the response from the model
        response = ""
        stream = ollama.chat(
            model=selected_model,
            messages=[{'role': 'user', 'content': user_input}],
            stream=True,
        )

        for chunk in stream:
            response += chunk['message']['content']
            text_area.insert("end", chunk['message']['content'])
            text_area.see("end")
            text_area.update()

        # Display the model's response in the chat area
        text_area.insert("end", "\n\n")
        text_area.configure(state="disabled")

    def about():
        easygui.msgbox("What is RYFAI?\n"
                       "RYFAI is a program that combines the power of AI with regards to a user's privacy. While AI companies have created outstanding AI\n"
                       "products, the flaws in these AI companies are very much there. Big Tech wants to infiltrate your privacy by selling your\n"
                       "private data to advertisers. Big Tech only wants the capital, and doesnt care about your privacy. So if Big Tech wont do it, then RYFAI will.\n"
                       "RYFAI is something different. RYFAI cares about it's user's data and doesn't use them like 'lab rats' for a profit.\n"
                       "RYFAI is in early development and is NOT open source (may change in the future). Ideas/inquiries for the RYFAI project go to ryfai@proton.me")

    def save_as_png():
        # Save the entire window as a PNG image in the current folder
        current_directory = os.path.dirname(os.path.abspath(__file__))
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        width = x + root.winfo_width()
        height = y + root.winfo_height()
        ImageGrab.grab().crop((x, y, width, height)).save(os.path.join(current_directory, "chat.png"))
        easygui.msgbox("Chat saved as chat.png in the current folder")

    def save_as_text():
        # Save the text content of the chat area as a text file in the current folder
        current_directory = os.path.dirname(os.path.abspath(__file__))
        chat_content = text_area.get("1.0", "end-1c")
        with open(os.path.join(current_directory, "chat.txt"), "w") as file:
            file.write(chat_content)
        easygui.msgbox("Chat saved as chat.txt in the current folder")

    # Create a label to display the current model
    model_label = ctk.CTkLabel(root, text="Current Model: None", width=700, height=30, anchor="w")
    model_label.place(x=0, y=0)

    # Create a text area for model output
    text_area = ctk.CTkTextbox(root, width=700, height=370)
    text_area.insert("1.0", "This is where model output is\n")
    text_area.configure(state="disabled")  # Make the text area non-editable

    # Place the text area at a specific position
    text_area.place(x=0, y=30)
    
    # Create a multi-line text area for user input
    text_input = ctk.CTkTextbox(root, width=400, height=80)
    text_input.insert("1.0", "Write your input here")
    text_input.place(x=5, y=410)
    
    send_button = ctk.CTkButton(root, width=100, height=80, text="Ask", command=send)
    send_button.place(x=420, y=410)

    # Create a dropdown button for selecting models
    model_var = ctk.StringVar(value="Select a model")
    model_dropdown = ctk.CTkOptionMenu(root, values=list(model_descriptions.keys()), variable=model_var, command=show_model_description)
    model_dropdown.place(x=530, y=410)

    # Create a label to display the model description
    description_label = ctk.CTkLabel(root, text="", width=150, height=100, anchor="nw", justify="left", wraplength=150)
    description_label.place(x=530, y=450)  # Adjust the y-coordinate to place it directly below the dropdown button

    # Create a button to save the chat as a PNG image
    save_png_button = ctk.CTkButton(root, width=100, height=60, text="Save as PNG", command=save_as_png)
    save_png_button.place(x=5, y=500)

    # Create a button to save the chat as a text file
    save_text_button = ctk.CTkButton(root, width=100, height=60, text="Save as Text", command=save_as_text)
    save_text_button.place(x=110, y=500)
    
    how_to_use = ctk.CTkButton(root, width=100, height=60, text="How to use", command=howtouse)
    how_to_use.place(x=215, y=500)

    about_ryfai = ctk.CTkButton(root, width=100, height=60, text="About RYFAI", command=about)
    about_ryfai.place(x=320, y=500)

    root.mainloop()

if __name__ == "__main__":
    main()
