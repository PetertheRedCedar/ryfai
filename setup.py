import easygui
import os

def ryfai_setup():
    choice = easygui.buttonbox("Welcome to RYFAI, your **ultimate** private and free AI chat experience.\n"
                               "Let us begin setup.\n"
                               "Note: By running this program, you agree to the Terms and Conditions. **You need a sufficient CPU or and RTX 2070 or above to run this program smoothly.**\n"
                               "Licensed under the Apache 2.0 License\n. For more information about RYFAI, visit https://reclaimyourfreedomai.streamlit.app"
                               "Do you have an NVIDIA gpu?", "RYFAI basic setup", ["yes", "no"])

    if choice == "yes":
        nvidia_gpu_setup()
    elif choice == "no":
        cpu_setup()
    else:
        exit_prompt = easygui.buttonbox("Are you sure you want to exit?", "Exit?", ["yes", "no"])
        if exit_prompt == "yes":
            exit()
        elif exit_prompt == "no":
            ryfai_setup()
        else:
            ryfai_setup()

def create_ryfai_exec():
    with open("run_ryfai.cmd", "w+") as create_ryfai_executable:
        create_ryfai_executable.write("streamlit run ryfai.py")
        create_ryfai_executable.close()

def nvidia_gpu_setup():
    create_ryfai_exec()
    os.system("configure-nvidiagpu.bat")

def cpu_setup():
    create_ryfai_exec()
    os.system("configure-cpu.bat")

if __name__ == "__main__":
    ryfai_setup()
