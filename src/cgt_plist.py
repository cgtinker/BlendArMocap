import plistlib
import sys
from pathlib import Path
import bpy


def main():
    return
    print(sys.platform)
    if not sys.platform == 'darwin':
        return

    # check if plist exists
    plist = Path(bpy.app.binary_path).parent.parent / 'Info.plist'
    if not plist.is_file():
        return

    with open(str(plist), 'rb') as fp:
        plist_dict = plistlib.load(fp)
        print(plist_dict)

    usage_descriptor = plist_dict.get('NSCameraUsageDescription', None)
    if usage_descriptor is not None:
        plist_dict.remove('NSCameraUsageDescription')
        pass

    print("writing")
    with open(str(plist), 'wb') as fp:
        plist_dict['NSCameraUsageDescription'] = '$(PRODUCT_NAME) camera use'
        plistlib.dump(plist_dict, fp)


if __name__ == '__main__':
    main()
