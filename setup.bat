cd /d "C:\Users\lauri\Rovix"

py -m venv .venv

.venv\Scripts\activate

python -m pip install -U pip

pip install -r requirements.txt

git remote add origin https://github.com/lauritzgames/Rovix.git
git branch -M main