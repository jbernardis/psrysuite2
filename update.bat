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

echo Copying data directory from an old directory
venv\Scripts\python copydata.py

echo Loading configuration editor
cd current
..\venv\Scripts\python config\main.py

echo Update complete
