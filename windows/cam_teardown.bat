@echo off
echo Stopping all ffmpeg streaming processes...

for /f "tokens=2" %%a in ('tasklist ^| findstr ffmpeg.exe') do (
    echo Terminating PID %%a
    taskkill /F /PID %%a
)

echo Done.
