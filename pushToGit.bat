@echo off

cd /d "C:\Users\lauri\Rovix"

call .venv\Scripts\Activate.bat

pip freeze > requirements.txt

git add .
git commit -m "Update"
git push -u origin main

pause