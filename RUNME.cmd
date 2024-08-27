@echo off
goto install

:install
color 0b
title Installing RYFAI dependencies
echo Installing dependency Winget
curl.exe -L -o winget.appxbundle https://aka.ms/getwinget
powershell Add-AppxPackage .\winget.appxbundle
winget --version
echo Winget is installed!
echo
echo FOLLOW THE ON-SCREEN STEPS TO INSTALL OLLAMA
winget install Ollama.Ollama
echo Ollama is installed!
echo Dependencies successfully installed!
echo starting RYFAI. Enjoy!
ryfai_main.exe

				