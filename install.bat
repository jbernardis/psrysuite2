@ECHO OFF
if exist current\ (
  echo Directory "current" already exists.  Please rename it or remove it.
  exit /b
)

if not exist src\ (
  echo Directory "src" does not exist.  Did you extract the zip file?
  exit /b
)

echo Renaming src directory as current and creating output directories
rename src current
mkdir current\logs
mkdir current\output

echo Creating python virtual environment
python -m venv ./venv
.\venv\Scripts\python -m pip install wheel
.\venv\Scripts\python -m pip install -r requirements.txt

echo Loading configuration editor for the first time
cd current
..\venv\Scripts\python config\main.py --install

echo Installation complete
