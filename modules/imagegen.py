from diffusers import StableDiffusionPipeline
import torch
import subprocess
import re

def is_model_installed(model_name):
    """Checks if a model is installed locally."""
    try:
        installed_models = subprocess.check_output(["ollama", "list"], universal_newlines=True)
        return model_name in installed_models
    except subprocess.CalledProcessError:
        return False

def install_model_with_progress(model_name):
    """Installs a model with progress tracking."""
    print(f"Installing model '{model_name}'. Please wait...")
    process = subprocess.Popen(
        ["ollama", "pull", model_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8"
    )

    for line in process.stdout:
        line = line.strip()
        print(line)  # Replace Streamlit's st.write with print
        match = re.search(r'(\d+)%', line)
        if match:
            progress = int(match.group(1))
            print(f"Progress: {progress}%")  # Log progress

    process.wait()
    if process.returncode == 0:
        print(f"Model '{model_name}' successfully installed!")
    else:
        print(f"Failed to install model '{model_name}'. Please try again.")

def generate_image(user_input):
    """Generates an image based on user input using Stable Diffusion."""
    model_id = "CompVis/stable-diffusion-v1-4"

    # Check if the model is installed
    if not is_model_installed(model_id):
        install_model_with_progress(model_id)

    # Initialize the model
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")  # Auto-detect GPU or CPU

    # Generate an image from the user input
    prompt = f"NEVER GENERATE NSFW CONTENT! {user_input}"
    image = pipe(prompt).images[0]

    # Save the image locally
    output_path = "generated_image.png"
    image.save(output_path)

    return output_path
