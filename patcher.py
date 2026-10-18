"""
DailyCells Patcher & Installer
===============================
Surgically patches Dead Cells binaries (deadcells.exe and deadcells_gl.exe)
to redirect online Daily Challenge API calls to the local emulator server.

Original URL : https://dead-cells.com\0 (22 bytes)
Patched URL  : http://127.0.0.1:18050\0 (22 bytes)

Author: whoami-28
Repository: https://github.com/whoami-28/daily-cells
"""

import os
import sys
import shutil
import argparse
import ctypes
from ctypes import wintypes

OLD_URL = b"https://dead-cells.com\x00"
NEW_URL = b"http://127.0.0.1:18050\x00"

assert len(OLD_URL) == len(NEW_URL), "URL lengths must match exactly!"

FILES_TO_COPY = [
    "daily_server.py",
    "Launch_DeadCells.vbs",
    "Launch_DeadCells.bat",
]

def find_game_directory(user_hint=None):
    if user_hint and os.path.isdir(user_hint):
        if has_deadcells_exe(user_hint):
            return os.path.abspath(user_hint)

    # 1. Current working directory or script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if has_deadcells_exe(script_dir):
        return script_dir

    cwd = os.getcwd()
    if has_deadcells_exe(cwd):
        return cwd

    # 2. Common install locations
    common_paths = [
        r"C:\Program Files (x86)\Steam\steamapps\common\Dead Cells",
        r"D:\SteamLibrary\steamapps\common\Dead Cells",
        r"E:\SteamLibrary\steamapps\common\Dead Cells",
        r"C:\GOG Games\Dead Cells",
        r"D:\GOG Games\Dead Cells",
        r"D:\03_InstDistrib\Dead Cells",
        r"C:\Games\Dead Cells",
        r"D:\Games\Dead Cells",
    ]
    for p in common_paths:
        if os.path.isdir(p) and has_deadcells_exe(p):
            return os.path.abspath(p)

    return None

def has_deadcells_exe(folder):
    return (
        os.path.isfile(os.path.join(folder, "deadcells.exe")) or
        os.path.isfile(os.path.join(folder, "deadcells_gl.exe"))
    )

def patch_binary(filepath):
    filename = os.path.basename(filepath)
    if not os.path.isfile(filepath):
        print(f"[-] File not found: {filename}")
        return False

    with open(filepath, "rb") as f:
        data = f.read()

    if NEW_URL in data:
        print(f"[*] {filename}: Already patched.")
        return True

    count = data.count(OLD_URL)
    if count == 0:
        print(f"[-] {filename}: Target URL pattern not found. Possibly unsupported version or already modified.")
        return False

    # Create backup if not exists
    backup_path = filepath + ".bak"
    if not os.path.exists(backup_path):
        shutil.copy2(filepath, backup_path)
        print(f"[+] Created backup: {os.path.basename(backup_path)}")

    new_data = data.replace(OLD_URL, NEW_URL)
    with open(filepath, "wb") as f:
        f.write(new_data)

    print(f"[+] {filename}: Successfully patched ({count} occurrence(s) redirected to {NEW_URL.decode()[:-1]}).")
    return True

def restore_binary(filepath):
    filename = os.path.basename(filepath)
    backup_path = filepath + ".bak"

    if os.path.exists(backup_path):
        shutil.copy2(backup_path, filepath)
        print(f"[+] {filename}: Restored from backup {os.path.basename(backup_path)}.")
        return True

    if not os.path.isfile(filepath):
        print(f"[-] File not found: {filename}")
        return False

    with open(filepath, "rb") as f:
        data = f.read()

    if NEW_URL in data:
        new_data = data.replace(NEW_URL, OLD_URL)
        with open(filepath, "wb") as f:
            f.write(new_data)
        print(f"[+] {filename}: Restored original URL in binary.")
        return True

    print(f"[*] {filename}: File is not patched or already in original state.")
    return True

def create_desktop_shortcut(game_dir):
    try:
        import win32com.client # if available
        # If not, use PowerShell or VBS
    except ImportError:
        pass

    # Use PowerShell to create .lnk
    vbs_target = os.path.join(game_dir, "Launch_DeadCells.vbs")
    exe_target = os.path.join(game_dir, "deadcells.exe")
    if not os.path.exists(exe_target):
        exe_target = os.path.join(game_dir, "deadcells_gl.exe")

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.exists(desktop):
        # Check OneDrive Desktop
        onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        if os.path.exists(onedrive_desktop):
            desktop = onedrive_desktop

    shortcut_path = os.path.join(desktop, "Dead Cells (Daily Challenge).lnk")
    game_lnk = os.path.join(game_dir, "Launch Dead Cells.lnk")

    ps_code = f"""
$ws = New-Object -ComObject WScript.Shell
$s1 = $ws.CreateShortcut('{shortcut_path}')
$s1.TargetPath = '{vbs_target}'
$s1.WorkingDirectory = '{game_dir}'
$s1.IconLocation = '{exe_target},0'
$s1.Description = 'Dead Cells with Offline Daily Challenge Emulator'
$s1.Save()

$s2 = $ws.CreateShortcut('{game_lnk}')
$s2.TargetPath = '{vbs_target}'
$s2.WorkingDirectory = '{game_dir}'
$s2.IconLocation = '{exe_target},0'
$s2.Description = 'Dead Cells with Offline Daily Challenge Emulator'
$s2.Save()
"""
    try:
        import subprocess
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_code], capture_output=True, check=True)
        print(f"[+] Created Desktop shortcut: {shortcut_path}")
        print(f"[+] Created Game folder shortcut: {game_lnk}")
        return True
    except Exception as e:
        print(f"[-] Could not create shortcuts automatically: {e}")
        return False

def install(game_dir):
    print(f"\n==========================================")
    print(f" Installing DailyCells into: {game_dir}")
    print(f"==========================================")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Copy emulator files if different directory
    if os.path.abspath(script_dir) != os.path.abspath(game_dir):
        for fname in FILES_TO_COPY:
            src = os.path.join(script_dir, fname)
            dst = os.path.join(game_dir, fname)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
                print(f"[+] Copied {fname} to game directory.")

    # 2. Patch binaries
    for exe_name in ["deadcells.exe", "deadcells_gl.exe"]:
        full_path = os.path.join(game_dir, exe_name)
        if os.path.isfile(full_path):
            patch_binary(full_path)

    # 3. Create shortcuts
    create_desktop_shortcut(game_dir)

    print("\n[SUCCESS] DailyCells is installed and ready to play!")
    print("Launch the game using the desktop shortcut or 'Launch_DeadCells.vbs'.")

def uninstall(game_dir):
    print(f"\n==========================================")
    print(f" Uninstalling DailyCells from: {game_dir}")
    print(f"==========================================")

    # 1. Restore binaries
    for exe_name in ["deadcells.exe", "deadcells_gl.exe"]:
        full_path = os.path.join(game_dir, exe_name)
        if os.path.isfile(full_path):
            restore_binary(full_path)

    # 2. Remove shortcuts
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    onedrive_desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
    for d in [desktop, onedrive_desktop]:
        lnk = os.path.join(d, "Dead Cells (Daily Challenge).lnk")
        if os.path.exists(lnk):
            try:
                os.remove(lnk)
                print(f"[+] Removed shortcut: {lnk}")
            except Exception:
                pass

    print("\n[SUCCESS] DailyCells has been uninstalled. Original game files restored.")

def main():
    parser = argparse.ArgumentParser(description="Dead Cells Daily Challenge Patcher & Installer")
    parser.add_argument("--dir", help="Path to Dead Cells game folder")
    parser.add_argument("--install", action="store_true", help="Install patch and emulator files")
    parser.add_argument("--uninstall", action="store_true", help="Restore original binaries and remove shortcuts")
    args = parser.parse_args()

    game_dir = find_game_directory(args.dir)

    if not game_dir:
        print("[-] Could not automatically locate Dead Cells installation folder.")
        hint = input("Please enter the path to your Dead Cells folder: ").strip().strip('"')
        game_dir = find_game_directory(hint)

    if not game_dir or not has_deadcells_exe(game_dir):
        print("[-] Error: Valid Dead Cells directory not found (deadcells.exe missing).")
        sys.exit(1)

    print(f"[*] Target Dead Cells folder: {game_dir}")

    if args.uninstall:
        uninstall(game_dir)
    else:
        # Default action: install
        install(game_dir)

if __name__ == "__main__":
    main()
