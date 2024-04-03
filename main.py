#!/usr/bin/env python3
import tkinter as tk
import platform
import os
import time
import sys
import ctypes
import glob
import requests
import subprocess
import shutil
import msipl_installer
from zipfile import ZipFile

if platform.system().lower() != 'linux' and platform.system().lower() != 'windows' and platform.system().lower() != 'darwin':
    print(f'\nERR: Sorry your platform {platform.system()} is not supported\nSupported platforms are: Linux, Windows, MacOS (Darwin)\n')
    sys.exit(1)

possible_drive = ['-']
windows_disk_letter = {}
deviceID = {}
m=tk.Tk()
m.title('DC-ARK Maker')

var = tk.StringVar(m)
var.set(possible_drive[0])

if platform.system().lower() != 'linux' and platform.system().lower() != 'darwin':
    import wmi
    import psutil
    c = wmi.WMI()
    for drive in c.Win32_DiskDrive():
        if drive.MediaType == 'Removable Media':
            possible_drive.append('disk'+str(drive.Index))
            deviceID[f'disk{str(drive.Index)}'] = drive.DeviceID
        for part in psutil.disk_partitions():
            if 'removable' in psutil.disk_partitions():
                windows_disk_letter[f'disk{str(drive.Index)}'] = part.mountpoint.split(':')[0]


elif platform.system().lower() == 'linux':
    out = subprocess.Popen(["lsblk | awk '{if ($3 == 1 && $1 ~ /^[a-zA-Z]+$/) {print $1}}'"], shell=True, stdout=subprocess.PIPE)
    out = out.stdout.read().decode().splitlines()
    for i in out:
        possible_drive.append(i)
else:
    out = subprocess.Popen(["""diskutil list external | awk '/external/ { gsub(/\/dev\//, ""); print $1}'"""], shell=True, stdout=subprocess.PIPE)
    out = out.stdout.read().decode().splitlines()
    for i in out:
        possible_drive.append(i)

def cleanup() -> None:
    shutil.rmtree("661")
    os.remove('661.PBP')
    os.remove('661.PBP.dec')
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
        resp = requests.get('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-linux.zip', verify=False)
        with open('pspdecrypt-1.0-linux.zip', 'wb') as f:
            f.write(resp.content)
        with ZipFile('pspdecrypt-1.0-linux.zip', 'r') as zObject:
            zObject.extractall(path=f'{os.getcwd()}/')
        os.system('oschmod 755 pspdecrypt')
        x['state'] = "normal"
    elif platform.system() == 'Windows':
        resp = requests.get('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-windows.zip', verify=False)
        with open('pspdecrypt-1.0-windows.zip', 'wb') as f:
            f.write(resp.content)
        with ZipFile('pspdecrypt-1.0-windows.zip', 'r') as zObject:
            zObject.extractall(path=f'{os.getcwd()}\\')
        os.system('oschmod 755 pspdecrypt.exe')
        x['state'] = "normal"
    elif platform.system() == 'Darwin':
        resp = requests.get('https://github.com/John-K/pspdecrypt/releases/download/1.0/pspdecrypt-1.0-macos.zip', verify=False)
        with open('pspdecrypt-1.0-macos.zip', 'wb') as f:
            f.write(resp.content)
        with ZipFile('pspdecrypt-1.0-macos.zip', 'r') as zObject:
            zObject.extractall(path=f'{os.getcwd()}/')
        os.system('oschmod 755 pspdecrypt')
        x['state'] = "normal"
    else:
        print('\nERR: unsupported platform...\n')
        return

    # Download 6.61 OFW
    resp = requests.get('http://du01.psp.update.playstation.org/update/psp/image/us/2014_1212_6be8878f475ac5b1a499b95ab2f7d301/EBOOT.PBP', verify=False)
    with open('661.PBP', 'wb') as f:
        f.write(resp.content)

    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        os.system('./pspdecrypt -e 661.PBP')
        shutil.copytree("661/F0", "TM/DCARK", dirs_exist_ok=True)
        shutil.copytree("661/F1", "TM/DCARK", dirs_exist_ok=True)
    else:
        os.system('.\\pspdecrypt.exe -e 661.PBP')
        shutil.copytree("661\\F0\\", "TM\\DCARK\\", dirs_exist_ok=True)
        shutil.copytree("661\\F1\\", "TM\\DCARK\\", dirs_exist_ok=True)

    # Download msipl_installer from Draan (forked for macOS support)
    resp = requests.get('https://raw.githubusercontent.com/krazynez/msipl_installer/main/msipl_installer.py', verify=False)
    with open('msipl_installer.py', 'wb') as f:
        f.write(resp.content)

    if platform.system() == 'Linux':
        disk = var.get() + '1'
        get_mountpoint = subprocess.Popen(f"lsblk | awk '/{disk}/ {{print $7}}'", shell=True, stdout=subprocess.PIPE)
        get_mountpoint = str(get_mountpoint.stdout.read().decode().rstrip()) + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        shutil.copytree("TM", get_mountpoint, dirs_exist_ok=True)
        #os.system('oschmod 755 msipl_installer.py')
        #os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --clear')
        #os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --insert msipl.bin')
        msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, '', False, True ))
        msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, 'msipl.bin', False, False ))
        status.config(fg='green', text="DONE!")
    elif platform.system() == 'Darwin':
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{var.get()}'])
        subprocess.run(['sync'])
        time.sleep(2)
        msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, '', False, True ))
        msipl_installer.main(msipl_installer.Args(f'{var.get()}', False, 'msipl.bin', False, False ))
        subprocess.run(['diskutil', 'mount', f'/dev/{var.get()}s1'])
        subprocess.run(['sync'])
        time.sleep(2)
        get_mountpoint = subprocess.Popen("""mount | awk '/{var.get()}/ {{if ($4 != "type"){{print $3,$4}} else {{print $3}}}}'""", shell=True, stdout=subprocess.PIPE)
        get_mountpoint = str(get_mountpoint.stdout.read().decode().rstrip()) + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        shutil.copytree("TM", f"{get_mountpoint}", dirs_exist_ok=True)
        #os.system('sync')
        #os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --clear')
        #os.system(f'sudo python3 ./msipl_installer.py --devname {var.get()} --insert msipl.bin')
        # device, info, insert, extract, clear
        #os.system(f'sudo dd if=msipl.bin of=/dev/{var.get()} bs=512 seek=16')
        status.config(fg='green', text="DONE!")
    else:
        get_mountpoint = windows_disk_letter[var.get()] + ":\\TM\\"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        shutil.copytree("TM", f"{get_mountpoint}", dirs_exist_ok=True)
        os.system('oschmod 755 msipl_installer.py')
        os.system(f'python .\\msipl_installer.py --pdisk {int(deviceID[var.get()][-1])} --clear')
        os.system(f'python .\\msipl_installer.py --pdisk {int(deviceID[var.get()][-1])} --insert msipl.bin')
        status.config(fg='green', text="DONE!")

    b['text'] = "DONE!"
    x['state'] = "normal"

    cleanup()

if platform.system() == 'Linux' or platform.system() == 'Darwin':
    if os.geteuid() != 0:
        print('\nSorry this needs to run as root/admin!\n')
        sys.exit(1)
else:
    if ctypes.windll.shell32.IsUserAnAdmin() != 1:
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

