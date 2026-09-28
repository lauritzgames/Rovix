@echo off
cd /d "C:\Users\lauri\Rovix"
pip freeze > requirements.txt

git remote add origin https://github.com/lauritzgames/Rovix.git
git branch -M main
git push -u origin main

git add .
git commit -m "Update"
git push -u origin main

pause