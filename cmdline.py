#!/usr/bin/env python3
import platform
import os
import sys
import subprocess
import msipl_installer
import shutil



def main():
    if len(sys.argv) < 2:
        print('You need to specifiy a disk')
        sys.exit(1)
    if platform.system() == 'Linux':
        if sys.argv[1].endswith('1'):
            print(f'ERR: you need to specify just the disk not partition\n\nEX: {sys.argv[0]} sdc\n')
            sys.exit(1)
        disk = sys.argv[1] + '1'
        get_mountpoint = subprocess.Popen(f"lsblk | awk '/{disk}/ {{print $7}}'", shell=True, stdout=subprocess.PIPE)
        get_mountpoint = str(get_mountpoint.stdout.read().decode().rstrip()) + "/TM/"
        print('Copying TM Folder')
        shutil.copytree("TM", get_mountpoint, dirs_exist_ok=True)
        print('Clearing IPL')
        msipl_installer.main(msipl_installer.Args(f'{sys.argv[1]}', False, None, False, True ))
        print('Writing IPL')
        msipl_installer.main(msipl_installer.Args(f'{sys.argv[1]}', False, 'msipl.bin', False, False ))
    elif platform.system() == 'Darwin':
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{sys.argv[1]}'])
        subprocess.run(['sync'])
        time.sleep(2)
        msipl_installer.main(msipl_installer.Args(f'{sys.argv[1]}', False, 'msipl.bin', False, False ))
        print('Writing IPL')
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{sys.argv[1]}'])
        subprocess.run(['mkdir', '/Volumes/__psp__'])
        get_mountpoint = '/Volumes/__psp__'
        copypoint = get_mountpoint + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        subprocess.run(['mount', '-t', 'msdos', '-o', 'rw', f'/dev/{sys.argv[1]}s1', get_mountpoint])
        print('Copying TM Folder')
        shutil.copytree("TM", f"{copypoint}", dirs_exist_ok=True)
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{sys.argv[1]}'])
    else:
        import wmi
        import psutil
        c = wmi.WMI()
        deviceID = {}
        windows_disk_letter = {}
        for drive in c.Win32_DiskDrive():
            if drive.MediaType == 'Removable Media':
                #possible_drive.append('disk'+str(drive.Index))
                deviceID[f'disk{str(drive.Index)}'] = drive.DeviceID
        for part in psutil.disk_partitions():
            if 'removable' in psutil.disk_partitions():
                windows_disk_letter[f'disk{str(drive.Index)}'] = part.mountpoint.split(':')[0]


        get_mountpoint = windows_disk_letter[sys.argv[1]] + ":\\TM\\"
        print('Copying TM Folder')
        shutil.copytree("TM", f"{get_mountpoint}", dirs_exist_ok=True)
        print('Clearing IPL')
        msipl_installer.main(msipl_installer.Args(f'{int(deviceID[sys.argv[1]][-1]}', False, None, False, True ))
        print('Writing IPL')
        msipl_installer.main(msipl_installer.Args(f'{int(deviceID[sys.argv[1]][-1]}', False, 'msipl.bin', False, False ))

if __name__ == '__main__':
    main()
