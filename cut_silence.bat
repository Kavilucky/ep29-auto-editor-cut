@echo off
chcp 65001 >nul
setlocal

rem Drag a video file onto this bat. Output: <video>_cut.xml next to the source (Premiere Pro / DaVinci Resolve).
rem The source video is never re-encoded, moved or deleted: only an XML timeline is created.

if "%~1"=="" (
  echo Перетащите видеофайл на этот батник мышкой.
  pause
  exit /b 1
)

where auto-editor >nul 2>nul
if errorlevel 1 (
  echo ОШИБКА: auto-editor не найден в PATH. Установите: pip install auto-editor
  pause
  exit /b 1
)

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo ОШИБКА: ffmpeg не найден в PATH. Установите FFmpeg и добавьте папку bin в PATH.
  pause
  exit /b 1
)

echo Анализ тишины: "%~1"
auto-editor "%~1" --margin 0.2sec --export premiere -o "%~dpn1_cut.xml"
if errorlevel 1 (
  echo ОШИБКА: auto-editor завершился с ошибкой. Исходный файл не тронут.
  pause
  exit /b 1
)

echo Готово: "%~dpn1_cut.xml"
echo Откройте этот XML в Premiere Pro или DaVinci Resolve. Исходное видео не изменено.
pause
exit /b 0
