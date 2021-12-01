import sys
import os

# TODO: CHECK FOR WINDOWS / MAC
def main():
    bpy_path = ensure_pip()
    required_modules = [
        ["opencv-python", "cv2"],
        ["mediapipe", "mediapipe"]
    ]
    for module in required_modules:
        install_module(bpy_path, module)


def ensure_pip():
    """ Downloads and installs pip if not available. """
    
    bpy_path = sys.exec_prefix
    os.system(f'cd {bpy_path}')
    os.system(f'{bpy_path}/bin/python3.7m -m ensurepip')
    return bpy_path
    
    
def is_module_installed(bpy_path, module):
    """ Installes module to internal bpy python. """
    
    res = os.system(f'{bpy_path}/bin/python3.7m -c "import {module[1]}"')
    if res == 0:
        print('module is installed')
        return True
    else:
        print(f'\nattempt to install module {module[0]}...')
        return False


def install_module(bpy_path, module):
    if not is_module_installed(bpy_path, module):
        cmd = f'{bpy_path}/bin/python3.7m -m pip install {module[0]}'
        print(cmd)
        os.system(cmd)


if __name__ == "__main__":
    main()