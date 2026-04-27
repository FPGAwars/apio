import usb.core
import usb.backend.libusb1


def find_library(_):
    # For macos.
    return "/Users/user/.apio/packages/oss-cad-suite/lib/libusb-1.0.0.dylib"


backend = usb.backend.libusb1.get_backend(find_library=find_library)

devices = usb.core.find(find_all=True, backend=backend)

for device in devices:
    print()
    print(str(device))
    print()
