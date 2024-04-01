#!/usr/bin/env python3
import tkinter as tk
import wget
import platform
import os
import time
import sys
import subprocess
import shutil
from zipfile import ZipFile
possible_drive = ['-']
m=tk.Tk()
m.title('DC-ARK Maker')

var = tk.StringVar(m)
var.set(possible_drive[0])

if platform.system().lower() != 'linux':
    import wmi
    c = wmi.WMI()
    for drive in c.Win32_LogicalDisk():
        if drive.DriveType == 2:
            possible_drive.append(drive)
else:
    out = subprocess.Popen(["lsblk | awk '{if ($3 == 1 && $1 ~ /^[a-zA-Z]+$/) {print $1}}'"], shell=True, stdout=subprocess.PIPE)
    out = out.stdout.read().decode().splitlines()
    for i in out:
        possible_drive.append(i)

def toggle_run(toggle):
    if toggle != '-':
        b['state'] = 'normal'
    else:
        b['state'] = 'disabled'

def run():
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
    else:
        wget.download('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-windows.zip')
        with ZipFile('pspdecrypt-1.0-windows.zip', 'r') as zObject:
            zObject.extractall(path=f'{os.getcwd()}\\')
        os.system('oschmod 755 pspdecrypt.exe')
        x['state'] = "normal"

    # Download 6.61 OFW
    wget.download('http://du01.psp.update.playstation.org/update/psp/image/us/2014_1212_6be8878f475ac5b1a499b95ab2f7d301/EBOOT.PBP')
    os.rename('EBOOT.PBP', '661.PBP')

    if platform.system() == 'Linux':
        os.system('./pspdecrypt -e 661.PBP')
        shutil.copytree("661/F0", "../TM/DCARK", dirs_exist_ok=True)
        shutil.copytree("661/F1", "../TM/DCARK", dirs_exist_ok=True)
    else:
        os.system('.\\pspdecrypt.exe -e 661.PBP')
        shutil.copytree("661\\F0\\", "..\\TM\\DCARK\\", dirs_exist_ok=True)
        shutil.copytree("661\\F1\\", "..\\TM\\DCARK\\", dirs_exist_ok=True)

    # Download msipl_installer from Draan
    wget.download('https://raw.githubusercontent.com/draanPSP/msipl_installer/main/msipl_installer.py')

    if platform.system() == 'Linux':
        os.system('oschmod 755 msipl_installer.py')
        os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --clear')
        os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --insert ../msipl.bin')
        disk = var.get() + '1'
        get_mountpoint = subprocess.Popen(f"lsblk | awk '/{disk}/ {{print $7}}'", shell=True, stdout=subprocess.PIPE)
        get_mountpoint = str(get_mountpoint.stdout.read().decode().rstrip()) + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        shutil.copytree("../TM", get_mountpoint, dirs_exist_ok=True)
        status.config(fg='green', text="DONE!")
    else:
        os.system('oschmod 755 msipl_installer.py')
        os.system(f'sudo python3 .\\msipl_installer.py --devname {var.get()} --clear')
        os.system('python3 .\\msipl_installer.py --devname {var.get()} --insert ..\\msipl.bin')
    b['text'] = "DONE!"
    x['state'] = "normal"

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

