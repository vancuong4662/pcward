@echo off

git config --global user.email "vancuong4662@gmail.com"
git config --global user.name "vancuong4662"

set /p commitMsg=Enter initial commit message: 
set /p repoUrl=Enter git repository URL: 

git init
git add .
git commit -m "%commitMsg%"
git branch -M master
git remote add origin %repoUrl%
git push -u origin master

echo Successfully first push to GitHub!
pause