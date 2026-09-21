# WiFi Analyzer Pro

> **نرم‌افزار حرفه‌ای آنالیز و پایش شبکه‌های وای‌فای برای ویندوز**  
> **Professional Windows Desktop WiFi Analyzer Application**

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg)](https://microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.12%2B-green.svg)](https://python.org)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-teal.svg)](https://www.qt.io)
[![Packaging](https://img.shields.io/badge/Packaging-PyInstaller-orange.svg)](https://pyinstaller.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

---

## فهرست مطالب / Table of Contents

- [بخش اول: مستندات فارسی (Persian Documentation)](#بخش-اول-مستندات-فارسی-persian-documentation)
  - [۱. معرفی پروژه](#۱-معرفی-پروژه)
  - [۲. ویژگی‌ها و امکانات کلیدی](#۲-ویژگی‌ها-و-امکانات-کلیدی)
  - [۳. پیش‌نیازهای سیستمی](#۳-پیش‌نیازهای-سیستمی)
  - [۴. نصب و راه‌اندازی](#۴-نصب-و-راه‌اندازی)
  - [۵. اجرای برنامه از سورس‌کد](#۵-اجرای-برنامه-از-سورس‌کد)
  - [۶. ساخت فایل اجرایی مستقل (.exe)](#۶-ساخت-فایل-اجرایی-مستقل-exe)
  - [۷. راهنمای استفاده از برنامه](#۷-راهنمای-استفاده-از-برنامه)
  - [۸. ساختار پروژه](#۸-ساختار-پروژه)
  - [۹. فناوری‌ها و ابزارهای مورد استفاده](#۹-فناوری‌ها-و-ابزارهای-مورد-استفاده)
  - [۱۰. عیب‌یابی و پرسش‌های متداول](#۱۰-عیب‌یابی-و-پرسش‌های-متداول)
  - [۱۱. لایسنس](#۱۱-لایسنس)
- [Part 2: English Documentation](#part-2-english-documentation)
  - [1. Project Overview](#1-project-overview)
  - [2. Key Features](#2-key-features)
  - [3. System Requirements](#3-system-requirements)
  - [4. Installation](#4-installation)
  - [5. Running from Source](#5-running-from-source)
  - [6. Building the Windows Executable (.exe)](#6-building-the-windows-executable-exe)
  - [7. Usage Guide](#7-usage-guide)
  - [8. Project Structure](#8-project-structure)
  - [9. Technologies & Architecture](#9-technologies--architecture)
  - [10. Troubleshooting & FAQ](#10-troubleshooting--faq)
  - [11. License](#11-license)

---

# بخش اول: مستندات فارسی (Persian Documentation)

## ۱. معرفی پروژه

نرم‌افزار **WiFi Analyzer Pro** یک ابزار رومیزی (Desktop) پیشرفته، مدرن و حرفه‌ای برای پایش، اسکن و تحلیل سیگنال‌های شبکه‌های بی‌سیم (WiFi) در محیط ویندوز است. این نرم‌افزار به صورت کامل و از پایه با زبان **پایتون (Python 3.12+)** و فریم‌ورک قدرتمند رابط کاربری **PySide6 (Qt for Python)** توسعه یافته است.

این برنامه بدون نیاز به هیچ‌گونه سخت‌افزار جانبی یا دانگل اختصاصی، با استفاده از دستور استاندارد و داخلی ویندوز:
```cmd
netsh wlan show networks mode=bssid
```
تمامی شبکه‌های اطراف، اکسس‌پوینت‌ها (Access Points)، روترهای چندبانده (Dual-Band / Mesh) و شبکه‌های مخفی را شناسایی کرده و اطلاعات دقیق آن‌ها را در قالبی چشم‌نواز با تم تیره (Dark Mode) و ابزارهای بصری تحلیلی به کاربر نمایش می‌دهد.

---


### رادار گرافیکی ۳۶۰ درجه متحرک (Radar Sweep)
* شبیه‌سازی رادار فرودگاهی با اشعه پایش چرخان (Sweep Beam) با نرخ فریم روان (۳۰ فریم بر ثانیه) و حداقل مصرف پردازنده (کمتر از ۱٪).
* ترسیم دایره‌های فاصله‌سنج متحدالمرکز بر حسب قدرت سیگنال (dBm-).
* چینش متوازن نقاط شبکه‌ها در ۳۶۰ درجه به همراه برچسب نام و درصد سیگنال.
* قابلیت توقف و فعال‌سازی مجدد انیمیشن رادار.


### نمودار مقایسه‌ای قدرت سیگنال (Signal Strength Chart)
* نمودار میله‌ای افقی زیبا با گرادیان رنگی منطبق بر کیفیت سیگنال (سبز/فیروزه‌ای برای سیگنال عالی، زرد برای متوسط، قرمز برای ضعیف).
* نمایش هم‌زمان درصد سیگنال و توان دریافتی به دسی‌بل میلی‌وات (RSSI dBm).
* قابلیت اسکرول نرم و مقایسه بصری سریع شبکه‌ها.

### جدول پیشرفته و فیلترپذیر شبکه‌ها (Networks Table)
* ستون‌های تفصیلی: SSID، آدرس فیزیکی BSSID (MAC)، درصد سیگنال، کانال، باند فرکانسی، امنیت/رمزنگاری، استاندارد رادیویی (802.11ax/ac/n/g/b) و نام شرکت سازنده چیپ/روتر (Vendor).
* نمایش نشانگرهای بلوکی سیگنال (مانند `████████░░`).
* جستجو و فیلتر آنی بر اساس نام، مک‌آدرس، باند یا کانال.
* کلیک‌راست برای کپی سریع SSID، مک‌آدرس یا کل مشخصات شبکه.

### پایگاه داده آفلاین شناسایی سازنده سخت‌افزار (OUI Lookup)
* شناسایی سازندگان روتر و چیپست از روی ۳ بایت اول مک‌آدرس (Apple, TP-Link, Netgear, Asus, Cisco, Ubiquiti, Huawei, D-Link, Google, Samsung, FRITZ!Box, Raspberry Pi, Espressif و...).

### خروجی گرفتن از داده‌ها (CSV & JSON Export)
* قابلیت ذخیره و استخراج نتایج اسکن به فرمت استاندارد CSV و JSON جهت گزارش‌گیری مهندسی شبکه.

### اسکن نامتقارن و بدون فریز با QThread
* بهره‌گیری از معماری چندنخی (Multi-threading) برای جلوگیری از هرگونه هنگ کردن یا قفل شدن موقت رابط کاربری در حین اسکن.

### حالت نمایشی (Demo Mode)
* سوییچ داخلی برای تولید داده‌های واقعی تست به منظور ارزیابی تمامی قابلیت‌های نرم‌افزار روی ماشین‌های مجازی (VM) یا سیستم‌های فاقد کارت وای‌فای فیزیکی.

---

## ۳. پیش‌نیازهای سیستمی

* **سیستم‌عامل:** ویندوز ۱۰ یا ویندوز ۱۱ (نسخه ۶۴ بیتی).
* **پایتون (در صورت اجرا از سورس):** Python 3.12 یا جدیدتر.
* **کارت شبکه بی‌سیم (Wi-Fi Adapter):** روشن و فعال در ویندوز.
* **دسترسی‌های کاربری:** کاربر استاندارد ویندوز (بدون نیاز به دسترسی Administrator).

---

## ۴. نصب و راه‌اندازی

### مرحله اول: دانلود یا کلون پروژه
```bash
git clone https://github.com/your-username/WiFiAnalyzerPro.git
cd WiFiAnalyzerPro
```

### مرحله دوم: ساخت و فعال‌سازی محیط مجازی پایتون (توصیه می‌شود)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### مرحله سوم: نصب وابستگی‌ها
```powershell
pip install -r requirements.txt
```

فایل `requirements.txt` تنها شامل وابستگی‌های حداقلی و ضروری است:
```text
PySide6>=6.5.0
pyinstaller>=6.0.0
```

---

## ۵. اجرای برنامه از سورس‌کد

برای اجرای مستقیم نرم‌افزار از طریق مفسر پایتون:
```powershell
python main.py
```

پس از اجرای دستور فوق، پنجره نرم‌افزار با تم تیره و مدرن باز شده و به صورت خودکار نخستین اسکن را انجام می‌دهد.

---

## ۶. ساخت فایل اجرایی مستقل (.exe)

برای ایجاد یک فایل اجرایی مستقل ویندوزی (`WiFiAnalyzerPro.exe`) که نیازی به نصب پایتون روی سیستم مقصد ندارد:

```powershell
python -m PyInstaller WiFiAnalyzerPro.spec --clean
```

### ویژگی‌های خروجی کامپایل شده:
* فایل نهایی در مسیر `dist/WiFiAnalyzerPro.exe` تولید می‌شود.
* پیکربندی `console=False` باعث می‌شود هیچ پنجره مشکی کنسولی هنگام اجرا باز نشود.
* تمامی آیکون‌ها، استایل‌ها، کتابخانه‌های Qt و ماژول‌های پایتون درون یک فایل EXE مجتمع قرار می‌گیرند.

---

## ۷. راهنمای استفاده از برنامه

1. **انجام اسکن:** با کلیک روی دکمه آبی‌رنگ بزرگ **SCAN** در گوشه بالا سمت راست، اسکن شبکه‌های وای‌فای اطراف آغاز می‌شود. در حین اسکن دکمه به وضعیت "SCANNING..." تغییر می‌یابد و پس از تکمیل، تمام ویجت‌ها به‌روزرسانی می‌شوند.
2. **بررسی خلاصه وضعیت در داشبورد:** پنج کارت خلاصه در بالای پنجره، تعداد کل شبکه‌ها، قوی‌ترین سیگنال، تعداد شبکه‌های ۲.۴ گیگاهرتز، شبکه‌های ۵ گیگاهرتز و کم‌ترافیک‌ترین کانال را نشان می‌دهند.
3. **مشاهده رادار:** با انتخاب تب **Radar Sweep**، موقعیت راداری شبکه‌ها و اشعه چرخشی متحرک را مشاهده کنید. برای متوقف کردن چرخش رادار، دکمه **Pause Radar** را بزنید.
4. **تحلیل طیفی کانال‌ها:** در تب **Channel Heatmap**، منحنی‌های هم‌پوشانی فرکانسی را برای کانال‌های ۱ تا ۱۴ (باند ۲.۴) و کانال‌های باند ۵ گیگاهرتز بررسی کنید تا بهترین کانال را برای روتر خود برگزینید.
5. **انتخاب و هایلایت مشترک:** با کلیک روی هر شبکه در جدول، رادار یا نمودارها، آن شبکه با خط حاشیه نورانی در تمام بخش‌های نرم‌افزار برجسته می‌شود.
6. **اسکن خودکار (Auto-Refresh):** از منوی کشویی Auto-Refresh می‌توانید بازه به‌روزرسانی خودکار را روی هر ۵ ثانیه، ۱۰ ثانیه یا ۳۰ ثانیه تنظیم کنید.
7. **استخراج داده‌ها:** با زدن دکمه **Export...**، نتایج اسکن را با قالب CSV یا JSON ذخیره نمایید.

---

## ۸. ساختار پروژه

```text
WiFiAnalyzerPro/
│
├── main.py                     # نقطه ورود اصلی نرم‌افزار
├── requirements.txt            # فهرست وابستگی‌های پایتون
├── README.md                   # مستندات دوزبانه (فارسی و انگلیسی)
├── WiFiAnalyzerPro.spec        # تنظیمات بسته‌بندی PyInstaller (بدون کنسول)
│
├── app/                        # پکیج اصلی برنامه
│   ├── __init__.py             # متادیتا و اطلاعات نسخه
│   ├── main_window.py          # پنجره اصلی، مدیریت رویدادها و تب‌ها
│   ├── scanner.py              # اسکنر شبکه‌ها و ورکر چندنخی (QThread)
│   ├── parser.py               # پردازشگر خروجی دستور netsh
│   ├── models.py               # مدل‌های داده‌ای WiFiNetwork و ScanResult
│   │
│   ├── widgets/                # ویجت‌های اختصاصی رابط کاربری
│   │   ├── __init__.py
│   │   ├── dashboard_cards.py  # کارت‌های خلاصه آماری داشبورد
│   │   ├── networks_table.py   # جدول شبکه‌ها با فیلتر و آیکون‌ها
│   │   ├── signal_chart.py     # نمودار میله‌ای گرافیکی قدرت سیگنال
│   │   ├── radar.py            # رادار ۳۶۰ درجه متحرک
│   │   └── heatmap.py          # نقشه حرارتی و منحنی‌های طیفی کانال‌ها
│   │
│   └── utils/                  # ابزارها و ماژول‌های کمکی
│       ├── __init__.py
│       ├── subprocess_utils.py # اجرای بی‌صدای زیرفرایندها (بدون کنسول)
│       ├── resources.py        # مدیریت مسیر فایل‌ها در حالت پکیج/سورس
│       ├── oui_lookup.py       # پایگاه داده سازندگان سخت‌افزار MAC
│       └── exporter.py         # خروجی‌گیر به CSV و JSON
│
├── assets/                     # دارایی‌های برنامه
│   ├── icons/                  # آیکون‌های برنامه در ابعاد مختلف (.ico و .png)
│   ├── styles/                 # استایل‌شیت تم تیره مدرن (dark_theme.qss)
│   └── screenshots/            # تصاویر پیش‌نمایش محیط برنامه
│
├── tests/                      # آزمون‌های واحد خودکار (Unit Tests)
│   ├── test_models.py
│   ├── test_parser.py
│   ├── test_scanner.py
│   ├── test_oui.py
│   └── test_export.py
│
└── dist/
    └── WiFiAnalyzerPro.exe     # فایل اجرایی نهایی ویندوز
```

---

## ۹. فناوری‌ها و ابزارهای مورد استفاده

| بخش | فناوری / کتابخانه | توضیحات |
| :--- | :--- | :--- |
| **زبان برنامه‌نویسی** | Python 3.12+ | ساختار شیءگرا، Type Hints و عملکرد بالا |
| **رابط کاربری (GUI)** | PySide6 (Qt 6.11) | ویجت‌های بومی، QPainter با Antialiasing و استایل QSS |
| **اسکن وای‌فای** | Windows `netsh wlan` | دستور بومی ویندوز بدون نیاز به درایور اضافه |
| **اجرای زیرفرایند** | Python `subprocess` | مدیریت شده با فلگ‌های `CREATE_NO_WINDOW` و `SW_HIDE` |
| **چندنخی** | Qt `QThread` | اسکن پس‌زمینه بدون مسدودسازی Thread اصلی رابط |
| **بسته‌بندی** | PyInstaller 6+ | تولید تک‌فایل اجرایی پرتابل با `console=False` |
| **آزمون‌های خودکار** | `pytest` / `unittest` | ۲۴ تست پوشش‌دهنده پارسر، مدل‌ها، ساب‌پراسس و خروجی‌ها |

---

## ۱۰. عیب‌یابی و پرسش‌های متداول

### ۱. پیام "WiFi adapter is unavailable" نمایش داده می‌شود:
* مطمئن شوید کارت شبکه بی‌سیم دستگاه روشن است و در حالت Airplane Mode قرار ندارد.
* سرویس `WLAN AutoConfig` ویندوز را از طریق `services.msc` بررسی کنید که در وضعیت Running باشد.
* برای آزمایش عملکرد برنامه روی سیستم‌های بدون وای‌فای، تیک گزینه **Demo Mode** را فعال کنید.

### ۲. آیا برای اجرای نرم‌افزار به اینترنت نیاز است؟
* خیر؛ این نرم‌افزار ۱۰۰٪ آفلاین است و هیچ ترافیک شبکه‌ای به اینترنت ارسال نمی‌کند.

### ۳. چرا هیچ پنجره کنسولی باز نمی‌شود؟
* این یکی از ملزومات کلیدی معماری این برنامه است. چه در زمان استارت و چه در زمان کلیک روی دکمه اسکن، تمامی فرآیندها با فلگ عدم نمایش پنجره (`CREATE_NO_WINDOW`) صدا زده می‌شوند.

---

## ۱۱. لایسنس

این پروژه تحت مجوز آزاد **MIT License** منتشر شده است و استفاده شخصی و تجاری از آن بلامانع است.

---

# Part 2: English Documentation

## 1. Project Overview

**WiFi Analyzer Pro** is a modern, standalone desktop wireless network analysis suite developed specifically for Microsoft Windows. Built with **Python 3.12+** and **PySide6 (Qt for Python)**, it inspects local wireless environments, monitors channel congestion, plots signal strength levels, and provides intuitive graphical diagnostics without requiring third-party scanning dongles or cloud dependencies.

All scans utilize the native Windows command:
```cmd
netsh wlan show networks mode=bssid
```
executed silently in the background with zero visible command prompts or flashing console windows.

---

## 2. Key Features

### Complete Console Window Suppression
* **No Console on Launch:** Compiled using PyInstaller with `console=False` (windowed mode). No command prompt, PowerShell, or console window flashes during application launch.
* **Silent Subprocess Execution:** WiFi scanning uses `subprocess.STARTUPINFO` with `wShowWindow = SW_HIDE` and `creationflags = CREATE_NO_WINDOW`. The scanner runs 100% invisibly in the background.

### 360-Degree Real-Time Animated Radar
* Continuous rotating sweep beam rendered at ~30 FPS with negligible CPU impact (< 1%).
* Concentric distance rings calibrated in dBm (-50 dBm to -90 dBm).
* Color-coded spatial blips denoting 2.4 GHz (amber), 5 GHz (cyan), and 6 GHz (purple) networks.
* One-click pause/resume toggle for zero-CPU environments.

### Channel Heatmap & Spectral Bell Curves
* Independent spectrum analysis tabs for **2.4 GHz** (Channels 1–14) and **5 GHz** (Channels 36–165).
* High-precision parabolic bell curves displaying channel bandwidth overlap (20 MHz / 40 MHz).
* Automated co-channel and adjacent-channel interference score calculation with non-overlapping channel recommendations (Channels 1, 6, 11).

### Graphical Signal Strength Visualizer
* High-DPI horizontal bar charts featuring smooth linear gradients representing signal quality tiers.
* Simultaneous readout of signal percentage and estimated RSSI in dBm (`RSSI ~= (Signal/2) - 100`).
* Dynamic hover inspection tooltips and interactive row selection.

### Comprehensive Networks Table
* Sortable and filterable data grid featuring columns for SSID, BSSID (MAC), Signal meter, Channel, Band, Authentication, Encryption, Radio type (802.11ax/ac/n/g/b), and Vendor.
* Real-time search filter matching SSIDs, MAC addresses, channels, or hardware vendors.
* Context menu with one-click clipboard copying.

### Offline Hardware Vendor Lookup (OUI)
* High-speed offline database resolving MAC address prefixes to manufacturers (Apple, Intel, TP-Link, Netgear, Asus, Cisco, Ubiquiti, Huawei, D-Link, Google, Samsung, FRITZ!Box, Raspberry Pi, Espressif, and more).

### Data Export (CSV & JSON)
* Instant export of discovered wireless networks and metadata to standard CSV and JSON files for engineering reports and network diagnostics.

### Non-Blocking Worker Architecture
* Powered by PySide6 `QThread`, ensuring the GUI remains responsive and fluid throughout background scanning cycles.

### Built-In Demo Mode
* Integrated simulation engine generating realistic dual-band wireless networks, enabling testing and review on virtual machines or PCs without wireless hardware.

---

## 3. System Requirements

* **Operating System:** Windows 10 or Windows 11 (64-bit).
* **Python Runtime (if running from source):** Python 3.12 or higher.
* **Network Hardware:** Active 802.11 wireless network adapter (or use Demo Mode).
* **Permissions:** Standard user privileges (no Administrator rights required).

---

## 4. Installation

### 1. Clone or Download Repository
```bash
git clone https://github.com/your-username/WiFiAnalyzerPro.git
cd WiFiAnalyzerPro
```

### 2. Set Up Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 5. Running from Source

To start the application directly from source:
```powershell
python main.py
```

The application initializes with the dark theme, opens the main dashboard, and initiates an initial wireless scan.

---

## 6. Building the Windows Executable (.exe)

Compile the application into a standalone Windows `.exe` using the customized spec file:

```powershell
python -m PyInstaller WiFiAnalyzerPro.spec --clean
```

### Packaging Highlights:
* Target Output: `dist/WiFiAnalyzerPro.exe`.
* Mode: Single-file windowed GUI (`console=False`).
* Embedded Resources: Application icons, Qt dark theme stylesheet, and core binaries bundled inside the executable.

---

## 7. Usage Guide

1. **Trigger Scan:** Click the prominent **SCAN** button in the top-right header. The button temporarily shifts to "SCANNING...", parses nearby access points, and refreshes all metrics.
2. **Review Metrics:** Check the five summary cards across the top for total networks, peak signal, band distribution, and the least congested 2.4 GHz channel.
3. **Radar Sweep:** Switch to the **Radar Sweep** tab to observe live spatial blips and sweep beam animation.
4. **Channel Spectrum:** Switch to **Channel Heatmap** to visualize channel occupancy bell curves and assess congestion across the 2.4 GHz and 5 GHz spectrum.
5. **Cross-Widget Selection:** Click any row in the table, blip in the radar, or bar in the chart to cross-highlight that specific network across all views.
6. **Auto-Refresh:** Enable scheduled background scanning by selecting an interval from the **Auto-Refresh** dropdown (5s, 10s, 30s).
7. **Export Results:** Click **Export...** to save scan results to a formatted CSV or JSON file.

---

## 8. Project Structure

```text
WiFiAnalyzerPro/
├── main.py                     # Application bootstrap and stylesheet loader
├── requirements.txt            # Python dependencies
├── README.md                   # Dual-language documentation (Persian & English)
├── WiFiAnalyzerPro.spec        # PyInstaller specification (console=False)
│
├── app/
│   ├── __init__.py             # Package version and metadata
│   ├── main_window.py          # Main UI coordinator, tabs, and timers
│   ├── scanner.py              # Silent netsh scanner and QThread worker
│   ├── parser.py               # Robust netsh text parser (multi-BSSID & hidden)
│   ├── models.py               # Data models: WiFiNetwork and ScanResult
│   │
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── dashboard_cards.py  # Summary metric cards
│   │   ├── networks_table.py   # Sortable/filterable table
│   │   ├── signal_chart.py     # Signal strength bar chart
│   │   ├── radar.py            # 360-degree radar visualizer
│   │   └── heatmap.py          # Channel spectral heatmap
│   │
│   └── utils/
│       ├── __init__.py
│       ├── subprocess_utils.py # Background hidden subprocess runner
│       ├── resources.py        # PyInstaller resource path resolver
│       ├── oui_lookup.py       # Hardware manufacturer dictionary
│       └── exporter.py         # CSV and JSON exporters
│
├── assets/
│   ├── icons/                  # Application icons (.ico and .png)
│   ├── styles/                 # Dark QSS stylesheet (dark_theme.qss)
│   └── screenshots/            # UI preview screenshots
│
├── tests/                      # Automated unit test suite
│   ├── test_models.py
│   ├── test_parser.py
│   ├── test_scanner.py
│   ├── test_oui.py
│   └── test_export.py
│
└── dist/
    └── WiFiAnalyzerPro.exe     # Standalone packaged Windows executable
```

---

## 9. Technologies & Architecture

* **Framework:** PySide6 (Qt 6.11) with QPainter antialiased rendering.
* **Process Management:** Subprocess with `CREATE_NO_WINDOW` (`0x08000000`) and `STARTUPINFO` (`SW_HIDE`).
* **Concurrency:** `QThread` event-driven worker with Qt signals (`scan_finished`, `scan_error`).
* **Packaging:** PyInstaller single-file bundle with PE32+ Windows GUI subsystem.
* **Testing:** 24 unit tests covering models, parsers, silent execution flags, and exporters.

---

## 10. Troubleshooting & FAQ

**Q: The application reports "WiFi adapter is unavailable".**  
A: Ensure your wireless network card is enabled in Windows Network Connections and not in Airplane Mode. If testing in a virtual machine or environment without WiFi hardware, check **Demo Mode** to test with simulated live data.

**Q: Does scanning require elevated (Administrator) permissions?**  
A: No. The standard Windows command `netsh wlan show networks mode=bssid` runs under standard user accounts.

**Q: How is console window appearance prevented?**  
A: On startup, PyInstaller sets the PE binary subsystem to GUI (`console=False`). During runtime scans, Python's `subprocess.run` receives `STARTUPINFO` configured with `SW_HIDE` and `creationflags=subprocess.CREATE_NO_WINDOW`, suppressing console window creation at the OS level.

---

## 11. License

This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it in personal or commercial environments.
