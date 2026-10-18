# DailyCells ⚔️🏰

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20(DirectX%20%7C%20OpenGL)-informational.svg)]()
[![Game Version](https://img.shields.io/badge/Dead%20Cells-v30--v35%2B-red.svg)]()

> **Автономный локальный эмулятор сервера Ежедневных испытаний (Daily Challenge / Daily Run) и таблицы лидеров для Dead Cells.**  
> *Offline autonomous emulator for Dead Cells Daily Challenge mode and leaderboard API.*

---

## 🇷🇺 Русский язык

### Описание проблемы
В игре **Dead Cells** режим «Ежедневные испытания» (Daily Challenge), открываемый Руной претендента после победы над Привратником, обращается к официальным серверам Motion Twin по адресу `https://dead-cells.com`.

Если серверы разработчиков отключены, заблокированы или недоступны, игра выдаёт **«Ошибку подключения к сети»** и не запускает забег, либо падает с фатальным исключением Haxe/HashLink (`$Lang.cleanUtf16String / Null access`).

### Решение
**DailyCells** — это автономное решение, которое:
1. **Перенаправляет сетевые вызовы игры**: Заменяет удалённый эндпоинт `https://dead-cells.com` на локальный `http://127.0.0.1:18050` в `deadcells.exe` и `deadcells_gl.exe`.
2. **Эмулирует бэкенд на 100%**:
   - Генерирует детерминированный сид забега на каждый календарный день.
   - Поддерживает строгую типизацию структур HashLink (`Type 1057`, `Type 1275`, `Type 23710`), что предотвращает любые падения интерфейса `LeaderboardPanel`.
   - Сохраняет ваши рекорды локально в `save/daily_scores.json`.
   - Позволяет просматривать результаты за предыдущие дни (`rewindDays`).
3. **Работает бесшовно**: Запускается в фоне без лишних черных окон и **автоматически выключается** сразу после закрытия игры (благодаря встроенному сторожевому таймеру Windows Toolhelp32).

---

### Быстрый старт (Установка в 1 клик)

#### Требования:
* Установленная игра **Dead Cells** (Steam, GOG или самостоятельная версия).
* **Python 3.8+** (при установке обязательно поставьте галочку *"Add Python to PATH"*).

#### Инструкция:
1. Скачайте репозиторий или релизный архив.
2. Запустите **`install.bat`**:
   - Скрипт сам найдёт папку с игрой (или попросит указать путь).
   - Сделает резервные копии оригинальных файлов (`.bak`).
   - Скопирует эмулятор и пропатчит `deadcells.exe` / `deadcells_gl.exe`.
   - Создаст ярлык **Dead Cells (Daily Challenge)** на Рабочем столе.
3. **Запустите игру через ярлык на Рабочем столе** и идите в дверь испытаний!

---

### Удаление
Чтобы полностью вернуть оригинальные файлы:
* Запустите **`uninstall.bat`** — он восстановит оригинальные исполняемые файлы из резервных копий `.bak` и удалит ярлыки.

---

### Структура проекта
* **`daily_server.py`** — локальный HTTP-сервер эмулятора с авто-завершением при выходе из игры.
* **`patcher.py`** — универсальный инструмент пропатчивания и восстановления бинарников.
* **`Launch_DeadCells.vbs`** — тихий запуск сервера и игры без всплывающих окон.
* **`Launch_DeadCells.bat`** — консольный лаунчер (альтернативный).
* **`install.bat`** — удобный установщик для пользователей.
* **`uninstall.bat`** — возврат оригинального состояния игры.

---

<br>

## en English

### The Problem
In **Dead Cells**, the *Daily Challenge* mode attempts to communicate with Motion Twin's online servers at `https://dead-cells.com`.

When the backend servers are unavailable, blocked, or offline, the game displays a **"Network Connection Error"** when entering the Daily Challenge door, or crashes with an uncaught HashLink exception (`Null access in $Lang.cleanUtf16String`).

### The Solution
**DailyCells** completely solves this by:
1. **Redirecting API calls**: Binary-patches `deadcells.exe` and `deadcells_gl.exe` to redirect `https://dead-cells.com` to `http://127.0.0.1:18050`.
2. **Local API Emulator**:
   - Generates unique deterministic seeds for each day.
   - Provides fully compliant HashLink typed responses (`Type 1057`, `Type 1275`, `Type 23710`) to eliminate `Null access` UI crashes.
   - Persists your daily personal best scores in `save/daily_scores.json`.
   - Supports day rewinding (`rewindDays`).
3. **Zero-Overhead Watchdog**: Runs silently in the background and automatically shuts down when `deadcells.exe` exits.

---

### Quick Start (1-Click Installation)

#### Requirements:
* **Dead Cells** (Steam, GOG, or standalone).
* **Python 3.8+** (make sure *"Add Python to PATH"* is checked during installation).

#### Steps:
1. Download or clone this repository.
2. Double-click **`install.bat`**:
   - Automatically detects your Dead Cells folder (or prompts for it).
   - Creates safe backups (`.bak`).
   - Patches executables and deploys the emulator files.
   - Creates a **Dead Cells (Daily Challenge)** shortcut on your Desktop.
3. Launch the game from the new desktop shortcut and enjoy your Daily Challenges!

---

### Uninstallation
To restore original unmodified game files:
* Run **`uninstall.bat`** to revert binaries from `.bak` backups and clean up shortcuts.

---

## License
MIT License. See [LICENSE](LICENSE) for details.
Dead Cells is a trademark of Motion Twin / Evil Empire. This project is an independent open-source emulator for offline preservation.
