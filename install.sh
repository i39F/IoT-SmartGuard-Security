#!/bin/bash
# ============================================================
#  SmartGuard — Installer Script
#  Run this on Kali Linux before using smartguard_gui.py
#  Usage: chmod +x install.sh && sudo bash install.sh
# ============================================================

GREEN='\033[0;32m'; CYAN='\033[0;36m'; RED='\033[0;31m'; NC='\033[0m'; BOLD='\033[1m'

echo ""
echo -e "${CYAN}${BOLD}"
echo "  ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗"
echo "  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝"
echo -e "${NC}"
echo -e "  ${CYAN}SmartGuard — Installer${NC}  |  Buraydah Colleges · Cybersecurity · 2025/2026"
echo ""

# ── Root check ───────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    echo -e "  ${RED}[✗] Please run as root:  sudo bash install.sh${NC}"
    exit 1
fi

echo -e "  ${GREEN}[✓] Running as root${NC}"
echo ""

# ── System update ─────────────────────────────────────────────
echo -e "  ${CYAN}[*] Updating package list…${NC}"
apt-get update -qq

# ── Install tools ─────────────────────────────────────────────
TOOLS=("aircrack-ng" "nmap" "xterm" "python3" "python3-pip")

for tool in "${TOOLS[@]}"; do
    if command -v "$tool" &>/dev/null; then
        echo -e "  ${GREEN}[✓] $tool — already installed${NC}"
    else
        echo -e "  ${CYAN}[*] Installing $tool…${NC}"
        apt-get install -y -qq "$tool"
        echo -e "  ${GREEN}[✓] $tool installed${NC}"
    fi
done

# ── Python dependency ─────────────────────────────────────────
echo ""
echo -e "  ${CYAN}[*] Installing Python GUI library (customtkinter)…${NC}"
pip3 install customtkinter -q
echo -e "  ${GREEN}[✓] customtkinter ready${NC}"

# ── Wordlist ──────────────────────────────────────────────────
echo ""
if [[ -f "/usr/share/wordlists/rockyou.txt" ]]; then
    echo -e "  ${GREEN}[✓] rockyou.txt already available${NC}"
elif [[ -f "/usr/share/wordlists/rockyou.txt.gz" ]]; then
    echo -e "  ${CYAN}[*] Decompressing rockyou.txt…${NC}"
    gunzip /usr/share/wordlists/rockyou.txt.gz
    echo -e "  ${GREEN}[✓] rockyou.txt ready${NC}"
else
    echo -e "  ${CYAN}[*] Installing wordlists…${NC}"
    apt-get install -y -qq wordlists
    gunzip /usr/share/wordlists/rockyou.txt.gz 2>/dev/null
    echo -e "  ${GREEN}[✓] Wordlist ready${NC}"
fi

# ── Permissions ───────────────────────────────────────────────
echo ""
echo -e "  ${CYAN}[*] Setting execute permissions…${NC}"
chmod +x smartguard.sh smartguard_gui.py 2>/dev/null
echo -e "  ${GREEN}[✓] Done${NC}"

# ── Summary ───────────────────────────────────────────────────
echo ""
echo -e "  ${GREEN}${BOLD}══════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}${BOLD}  Installation complete — SmartGuard is ready!${NC}"
echo -e "  ${GREEN}${BOLD}══════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Run the GUI:   ${CYAN}sudo python3 smartguard_gui.py${NC}"
echo -e "  Run the CLI:   ${CYAN}sudo bash smartguard.sh${NC}"
echo ""
echo -e "  ${RED}⚠  For authorized lab environments only.${NC}"
echo ""
