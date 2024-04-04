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
        shutil.copytree("TM", get_mountpoint, dirs_exist_ok=True)
        msipl_installer.main(msipl_installer.Args(f'{sys.argv[1]}', False, None, False, True ))
        msipl_installer.main(msipl_installer.Args(f'{sys.argv[1]}', False, 'msipl.bin', False, False ))
    elif platform.system() == 'Darwin':
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{sys.argv[1]}'])
        subprocess.run(['sync'])
        time.sleep(2)
        msipl_installer.main(msipl_installer.Args(f'{sys.argv[1]}', False, 'msipl.bin', False, False ))
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{sys.argv[1]}'])
        subprocess.run(['mkdir', '/Volumes/__psp__'])
        get_mountpoint = '/Volumes/__psp__'
        copypoint = get_mountpoint + "/TM/"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        subprocess.run(['mount', '-t', 'msdos', '-o', 'rw', f'/dev/{sys.argv[1]}s1', get_mountpoint])
        shutil.copytree("TM", f"{copypoint}", dirs_exist_ok=True)
        subprocess.run(['diskutil', 'umountDisk', 'force', f'/dev/{sys.argv[1]}'])
        status.config(fg='green', text="DONE!")
    else:
        get_mountpoint = windows_disk_letter[sys.argv[1]] + ":\\TM\\"
        status.config(text="COPYING PLEASE WAIT!")
        m.update()
        shutil.copytree("TM", f"{get_mountpoint}", dirs_exist_ok=True)
        os.system('oschmod 755 msipl_installer.py')
        os.system(f'python .\\msipl_installer.py --pdisk {int(deviceID[sys.argv[1]][-1])} --clear')
        os.system(f'python .\\msipl_installer.py --pdisk {int(deviceID[sys.argv[1]][-1])} --insert msipl.bin')
        status.config(fg='green', text="DONE!")

if __name__ == '__main__':
    main()
