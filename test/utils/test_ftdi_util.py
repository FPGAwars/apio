"""
Tests of ftd_util.py
"""

from apio.utils import ftdi_util

# Ignore long lines.
# flake8: noqa: E501

# -- Simulated 'openFPGALoader --scan-usb' output text.
# -- See issue https://github.com/trabucayre/openFPGALoader/issues/549
TEXT_WITH_DEVICES = """
empty
Bus device vid:pid       probe type      manufacturer serial               product
000 001    0x0403:0x6010 FTDI2232        AlhambraBits none                 Alhambra II v1.0A - B09-335
001 001    0x0403:0x6010 FTDI2232        tinyVision.ai FT94RQ8V             UPduino v3.1c
002 001    0x0403:0x6010 FTDI2232        tinyVision.ai.v3 FT94RQ8V             UPduino v3.1c
"""

# -- Text when no device is connected.
TEXT_NO_DEVICES = """
empty
No USB devices found
Bus device vid:pid       probe type      manufacturer serial               product
"""

# -- Per https://tinyurl.com/3wxeawkv , testing with both old and new names.
PROGRAM_TYPE_TITLES = ["probe type", "probe_type"]


def test_text_with_devices():
    """Test parsing of 'openFPGALoader --scan-usb' text that contains devices."""

    # pylint: disable=protected-access

    for title in PROGRAM_TYPE_TITLES:
        print(f"{title=}")

        text = TEXT_WITH_DEVICES.replace("probe type", title)

        devices = ftdi_util._get_devices_from_text(text)

        expected = [
            ftdi_util.DeviceInfo(
                index=0,
                bus=0,
                device=1,
                vendor_id="0403",
                product_id="6010",
                type="FTDI2232",
                manufacturer="AlhambraBits",
                serial_code="",
                description="Alhambra II v1.0A - B09-335",
            ),
            ftdi_util.DeviceInfo(
                index=1,
                bus=1,
                device=1,
                vendor_id="0403",
                product_id="6010",
                type="FTDI2232",
                manufacturer="tinyVision.ai",
                serial_code="FT94RQ8V",
                description="UPduino v3.1c",
            ),
            ftdi_util.DeviceInfo(
                index=2,
                bus=2,
                device=1,
                vendor_id="0403",
                product_id="6010",
                type="FTDI2232",
                manufacturer="tinyVision.ai.v3",
                serial_code="FT94RQ8V",
                description="UPduino v3.1c",
            ),
        ]

        assert devices == expected


def test_text_without_devices():
    """Test parsing of 'openFPGALoader --scan-usb' text that contains
    no devices."""

    # pylint: disable=protected-access
    # pylint: disable=use-implicit-booleaness-not-comparison

    for title in ["probe type", "probe_type"]:
        print(f"{title=}")

        text = TEXT_NO_DEVICES.replace("probe type", title)

        devices = ftdi_util._get_devices_from_text(text)

        assert devices == []
