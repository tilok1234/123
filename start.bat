@echo off
echo Starting Enemy Fight Planner Demo...
cd enemy-fight-planner

echo Installing dependencies...
call npm.cmd install

echo Running demo...
call npm.cmd start

pause
