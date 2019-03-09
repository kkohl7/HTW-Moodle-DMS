@echo off 
echo Das Programm wird gestartet. Dies kann einige Momente dauern. Bitte haben Sie Geduld!
SET mypath=%~dp0
SET python="%mypath%\venv\Scripts\python.exe" "%mypath%\Controller.py"
SET pythonInstallation="%mypath%\venv\Scripts\python.exe" "%mypath%\setup.py"
echo Es wird ueberprueft, ob Sie alle benoetigten Dateien zur Ausfuehrung haben.
%pythonInstallation%
echo Das Programm wird gestartet
%python%
