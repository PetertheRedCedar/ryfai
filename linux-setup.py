import easygui
import os

def install_ryfai():
	gpu_cpu = easygui.buttonbox("Welcome to RYFAI!\n"
				    "Good on you for choosing private AI!"
				    "More information on the RYFAI website https://ryfai.streamlit.app\n\n"
				    "Would you like to set up with an NVIDIA gpu or CPU only?\n\n",
				    "RYFAI setup.",
				    ["Set up with NVIDIA gpu", "Set up with CPU only"]
	)

	if gpu_cpu == "Set up with NVIDIA gpu":
		os.system("chmod +x install-gpu.sh")
		easygui.msgbox("RYFAI is successfully installed! Next time you want to run ryfai, just open your terminal where ryfai is located and type './ryfai.sh'!")
		os.system("./install-gpu.sh")
		create_executable()
	elif gpu_cpu == "Set up with CPU only":
		os.system("chmod +x install-cpu.sh")
		os.system("./install-cpu.sh")
		easygui.msgbox("RYFAI is successfully installed! Next time you want to run ryfai, just open your terminal where ryfai is located and type './ryfai.sh'!")
		create_executable()
	else:
		quit_choice = easygui.buttonbox("Quit?", "quit?", ["yes", "no"])
		if quit_choice == "yes":
			quit()
		elif quit_choice == "no":
			install_ryfai()
		else:
			quit()
			
def create_executable():
	with open("ryfai.sh", "w+") as start:
		start.write("streamlit run ryfai.py")
		start.close()
	os.system("chmod +x ryfai.sh")
	os.system("./ryfai.sh")

install_ryfai()
