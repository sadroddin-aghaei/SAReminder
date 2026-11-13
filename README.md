<div align="center">

# ⏰ SAReminder

**A fast, private, offline task manager and reminder app with a Persian (Jalali) calendar.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Qt](https://img.shields.io/badge/UI-PySide6%20(Qt)-41CD52?logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57?logo=sqlite&logoColor=white)
![Platforms](https://img.shields.io/badge/Windows%20x64%20%7C%20ARM64%20%7C%20macOS%20Intel%20%7C%20Apple%20Silicon-black)
![Language](https://img.shields.io/badge/UI-English%20%7C%20فارسی-ff3030)
![License](https://img.shields.io/badge/License-Personal%20Use%20Only-red)

OLED-black design · native notifications · works 100% offline · your data never leaves your device

</div>

---

## ✨ Features

| | |
|---|---|
| 🎨 **TickTick-style UI** | Sidebar with smart lists, round priority checkboxes, quick-add bar, clean task rows with due dates, tags and list chips |
| 🌈 **Custom theme color** | 8 presets or any custom color, applied instantly. Dark (OLED) or Light theme |
| ✨ **Animations** | Page fades, task-complete fade-out, count-up stats, animated chart and progress, focus ring, toasts, dialog and window fade-in (can be turned off) |
| ⚡ **Smart quick add** | Type `Call mom tomorrow 18:00 #family !!` and it sets the date, time, tag and priority for you |
| 📋 **Smart lists** | All, Today, Tomorrow, Next 7 Days, Overdue, Starred, Completed, with live counters |
| 🗂️ **Custom lists** | Create colored lists, move tasks between them, delete lists |
| ☑️ **Tasks** | Priorities, tags, notes, **checklists**, due date & time, starred, duplicate, edit, search, sort (date / priority / title / newest), right-click menu |
| 🔁 **Recurring tasks** | Daily, weekly or monthly. Completing one creates the next |
| 🔔 **Smart reminders** | At due time or 5 min – 1 day before, tray notification, sound, and a popup with **Snooze 10 min** and **Complete** |
| 📅 **Calendar** | Jalali (Shamsi) or Gregorian month view with task markers; click a day to see or add tasks |
| 📊 **Dashboard** | Today / overdue / completed counters, day streak, today's progress, 7-day completion chart, upcoming tasks |
| 🍅 **Focus timer** | Pomodoro with animated ring, adjustable focus/break, notifications, daily session count |
| 🔥 **Habits** | Daily check-in with a 7-day strip and streak |
| 📝 **Notes** | Instant auto-saved notes |
| 🌐 **Persian & RTL** | Full Persian UI, right-to-left layout, Persian digits, Jalali dates |
| ⚙️ **Settings** | Accent color, theme, animations, sound, language, calendar system, 12/24-hour, default reminder, start with Windows, JSON backup & restore |
| 🔔 **Icon** | A bell (reminder) app icon that follows your theme color |

## ⌨️ Keyboard shortcuts

Active while the app window is focused.

| Shortcut | Action |
|---|---|
| `Ctrl + N` | New task (dialog) |
| `Ctrl + F` | Search tasks |
| `Ctrl + 1` … `Ctrl + 7` | Today, Dashboard, Calendar, Focus, Habits, Notes, Settings |
| `Delete` | Delete the selected task |

## 📥 Download

Grab the latest build from the **[Releases](../../releases)** page:

| Platform | File |
|---|---|
| Windows 10/11 (Intel/AMD 64-bit) | `SAReminder-<version>-windows-x64.zip` |
| Windows 11 on ARM | `SAReminder-<version>-windows-arm64.zip` |
| macOS (Intel) | `SAReminder-<version>-macos-intel.dmg` |
| macOS (Apple Silicon) | `SAReminder-<version>-macos-apple-silicon.dmg` |

> **Windows:** unzip and run `SAReminder.exe`. SmartScreen may warn because the app is not code-signed: click *More info → Run anyway*.
> **macOS:** drag the app to Applications. First launch: right-click → *Open* (the app is not notarized).

## 🛠️ Run from source

Requires Python 3.10+.

```bash
git clone https://github.com/<your-username>/<repo>.git
cd <repo>
python -m venv .venv
# Windows:  .venv\Scripts\activate      macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Start minimized to the tray: `python app.py --hidden`

## 📦 Build an executable

```bash
python make_icon.py
pyinstaller --noconfirm --windowed --name SAReminder --icon assets/icon.ico app.py   # Windows
pyinstaller --noconfirm --windowed --name SAReminder --icon assets/icon.icns app.py  # macOS
```

Output goes to `dist/`.

## 🚀 Automated releases (GitHub Actions)

Pushing a version tag builds all four targets in parallel and attaches them to a **draft release** with auto-generated notes.

```bash
git tag v3.0.0
git push origin v3.0.0
```

Then open **Releases**, review the draft and click **Publish release**.

| Target | Runner |
|---|---|
| Windows x64 | `windows-latest` |
| Windows ARM64 | `windows-11-arm` |
| macOS Apple Silicon | `macos-latest` |
| macOS Intel | `macos-15-intel` |

Workflow: [`.github/workflows/release.yml`](.github/workflows/release.yml). You can also run it manually from the **Actions** tab.

## 🔒 Privacy & data

- No accounts, no telemetry, no network access.
- Everything is stored locally in `~/.sareminder/sareminder.db` (SQLite). Use **Settings → Open data folder** to find it.
- **Settings → Export JSON backup** saves tasks, habits and notes; **Import** restores them.

## ⚠️ Good to know

- Reminders fire while the app is running (window open or minimized to the tray). If you fully quit from the tray menu, reminders pause until you start it again. Enable **Start with Windows** to avoid missing any.
- Windows ARM64 builds depend on PySide6 support for that platform and are the most experimental target.
- The Jalali calendar uses a built-in algorithm (no internet needed) valid for modern dates.

## 🗺️ Roadmap

- [ ] Day / week / year calendar views
- [ ] Drag & drop events and tasks
- [ ] Global (system-wide) hotkeys
- [ ] Windows installer and signed builds

## 🗂️ Project structure

```
├── app.py                      # the whole application
├── make_icon.py                # generates .ico / .icns icons
├── requirements.txt
├── LICENSE
└── .github/workflows/release.yml
```

## 🇮🇷 به فارسی

**SAReminder** یک برنامه‌ی مدیریت وظایف و یادآور آفلاین با تقویم شمسی است. داده‌ها فقط روی دستگاه خودتان ذخیره می‌شوند.

- داشبورد، وظایف با اولویت، برچسب و تکرار، یادآوری با اعلان و تعویق ۱۰ دقیقه‌ای
- تقویم جلالی و میلادی، تایمر تمرکز (پومودورو)، عادت‌ها و یادداشت‌ها
- رابط کاملاً فارسی و راست‌به‌چپ با ارقام فارسی
- پشتیبان‌گیری و بازیابی با JSON
- بستن پنجره، برنامه را به سینی سیستم می‌برد تا یادآوری‌ها ادامه پیدا کنند

برای دانلود به بخش **Releases** بروید و فایل مناسب سیستم خود را بگیرید. زبان را از **تنظیمات** عوض کنید.

## 📄 License

**Universal Proprietary Software & Project License v1.0 — Personal Use Only.**
Copyright © 2026 Sadroddin Aghaei. All Rights Reserved.

Personal, non-commercial use is permitted. Redistribution, publishing modified versions and commercial use require prior written permission from the copyright owner. See [LICENSE](LICENSE) for the full terms.

## 👨‍💻 Author

**Sadroddin Aghaei** · [github.com/sadroddin-aghaei](https://github.com/sadroddin-aghaei)

<div align="center">

© Copyright © Sadroddin Aghaei. All Rights Reserved.

</div>
