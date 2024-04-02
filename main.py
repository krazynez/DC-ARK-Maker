#!/usr/bin/env python3
import tkinter as tk
import wget
import platform
import os
import time
import sys
import glob
import subprocess
import shutil
from zipfile import ZipFile

if platform.system().lower() != 'linux' and platform.system().lower() != 'windows' and platform.system().lower() != 'darwin':
    print(f'\nERR: Sorry your platform {platform.system()} is not supported\nSupported platforms are: Linux, Windows, MacOS (Darwin)\n')
    sys.exit(1)

possible_drive = ['-']
windows_disk_letter = []
m=tk.Tk()
m.title('DC-ARK Maker')

var = tk.StringVar(m)
var.set(possible_drive[0])

if platform.system().lower() != 'linux' and platform.system().lower() != 'darwin':
    import wmi
    c = wmi.WMI()
    for drive in c.Win32_LogicalDisk():
        if drive.DriveType == 2:
            possible_drive.append(drive)
            windows_disk_letter.append(drive.caption)
elif platform.system().lower() == 'linux':
    out = subprocess.Popen(["lsblk | awk '{if ($3 == 1 && $1 ~ /^[a-zA-Z]+$/) {print $1}}'"], shell=True, stdout=subprocess.PIPE)
    out = out.stdout.read().decode().splitlines()
    for i in out:
        possible_drive.append(i)
else:
    out = subprocess.Popen(["diskutil list external | awk '/external/ { gsub(/\/dev\//, ""); print $1}'"], shell=True, stdout=subprocess.PIPE)
    out = out.stdout.read().decode().splitlines()
    for i in out:
        possible_drive.append(i)

def cleanup() -> None:
    shutil.rmtree("661")
    os.remove('661.PBP')
    os.remove('661.PBP.dec')
    os.remove('msipl_installer.py')
    for f in glob.glob("pspdecrypt*"):
        os.remove(f)

def toggle_run(toggle) -> None:
    if toggle != '-':
        b['state'] = 'normal'
    else:
        b['state'] = 'disabled'

def run() -> None:
    b['state'] = "disabled"
    x['state'] = "disabled"
    b['text'] = "Please Wait..."

    # Download pspdecrypt from John
    if platform.system() == 'Linux':
        wget.download('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-linux.zip')
        with ZipFile('pspdecrypt-1.0-linux.zip', 'r') as zObject:
            zObject.extractall(path=f'{os.getcwd()}/')
        os.system('oschmod 755 pspdecrypt')
        x['state'] = "normal"
    elif platform.system() == 'Windows':
        wget.download('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-windows.zip')
        with ZipFile('pspdecrypt-1.0-windows.zip', 'r') as zObject:
            zObject.extractall(path=f'{os.getcwd()}\\')
        os.system('oschmod 755 pspdecrypt.exe')
        x['state'] = "normal"
    elif platform.system() == 'Darwin':
        wget.download('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-macos.zip')
        with ZipFile('pspdecrypt-1.0-macos.zip', 'r') as zObject:
            zObject.extractall(path=f'{os.getcwd()}/')
        os.system('oschmod 755 pspdecrypt')
        x['state'] = "normal"
    else:
        print('\nERR: unsupported platform...\n')
        return

    # Download 6.61 OFW
    wget.download('http://du01.psp.update.playstation.org/update/psp/image/us/2014_1212_6be8878f475ac5b1a499b95ab2f7d301/EBOOT.PBP')
    os.rename('EBOOT.PBP', '661.PBP')

    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        os.system('./pspdecrypt -e 661.PBP')
        shutil.copytree("661/F0", "TM/DCARK", dirs_exist_ok=True)
        shutil.copytree("661/F1", "TM/DCARK", dirs_exist_ok=True)
    else:
        os.system('.\\pspdecrypt.exe -e 661.PBP')
        shutil.copytree("661\\F0\\", "TM\\DCARK\\", dirs_exist_ok=True)
        shutil.copytree("661\\F1\\", "TM\\DCARK\\", dirs_exist_ok=True)

    # Download msipl_installer from Draan
    wget.download('https://raw.githubusercontent.com/draanPSP/msipl_installer/main/msipl_installer.py')

    if platform.system() == 'Linux':
        os.system('oschmod 755 msipl_installer.py')
        os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --clear')
        os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --insert msipl.bin')
        disk = var.get() + '1'
        get_mountpoint = subprocess.Popen(f"lsblk | awk '/{disk}/ {{print $7}}'", shell=True, stdout=subprocess.PIPE)
        get_mountpoint = str(get_mountpoint.stdout.read().decode().rstrip()) + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        shutil.copytree("TM", get_mountpoint, dirs_exist_ok=True)
        status.config(fg='green', text="DONE!")
    elif platform.system() == 'Darwin':
        os.system('oschmod 755 msipl_installer.py')
        os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --clear')
        os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --insert msipl.bin')
        get_mountpoint = subprocess.Popen(f"mount | awk '/\/dev\/{var.get()}/ {{print $3}}'", shell=True, stdout=subprocess.PIPE)
        get_mountpoint = str(get_mountpoint.stdout.read().decode().rstrip()) + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        shutil.copytree("TM", f"'{get_mountpoint}'", dirs_exist_ok=True)
        status.config(fg='green', text="DONE!")
    else:
        os.system('oschmod 755 msipl_installer.py')
        os.system(f'python3 .\\msipl_installer.py --devname {var.get()} --clear')
        os.system(f'python3 .\\msipl_installer.py --devname {var.get()} --insert msipl.bin')
        get_index = possible_drive.index(var.get())
        get_mountpoint = windows_disk_letter[get_index] + "\\TM\\"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        shutil.copytree("TM", f"'{get_mountpoint}'", dirs_exist_ok=True)
        status.config(fg='green', text="DONE!")

    b['text'] = "DONE!"
    x['state'] = "normal"

    cleanup()

if os.geteuid() != 0:
    print('\nSorry this needs to run as root/admin!\n')
    sys.exit(1)

# Setup
m.minsize(320, 120)

disk = tk.OptionMenu(m, var, *possible_drive, command=toggle_run)
disk.grid(row=0,column=1)
tk.Label(text="Select PSP/Memory Stick:", width=25).grid(row=0, column=0)
status = tk.Label(fg='red', text="PLEASE VERIFY\nDISK BEFORE CONTINUING!", width=25)
status.grid(row=1, column=0)

b=tk.Button(m, text='Run', command=run)
b.grid(row=1,column=1)
x=tk.Button(m, text='Exit', command=m.destroy)
x.grid(row=2,column=1)

if var.get() == '-':
    b['state'] = 'disabled'

   

m.mainloop()

