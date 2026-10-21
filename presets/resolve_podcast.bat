@echo off
chcp 65001 >nul
setlocal

rem PRESET: DaVinci Resolve, podcast
rem Drag a video file onto this bat. Output: <video>_resolve.fcpxml next to the source (DaVinci Resolve (Файл, Импорт, Таймлайн)).
rem The source video is never re-encoded, moved or deleted: only a timeline file is created.
rem Start values (threshold 4%, margin 0.2sec) are a starting point: tune them for your recording.

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

echo Пресет: DaVinci Resolve, подкаст и студийная речь
echo Анализ тишины: "%~1"
auto-editor "%~1" --edit audio:threshold=4% --margin 0.2sec --export resolve -o "%~dpn1_resolve.fcpxml"
if errorlevel 1 (
  echo ОШИБКА: auto-editor завершился с ошибкой. Исходный файл не тронут.
  echo Проверьте синтаксис флагов для вашей версии: auto-editor --help
  pause
  exit /b 1
)

echo Готово: "%~dpn1_resolve.fcpxml"
echo Импортируйте файл в DaVinci Resolve (Файл, Импорт, Таймлайн). Исходное видео не изменено.
pause
exit /b 0
