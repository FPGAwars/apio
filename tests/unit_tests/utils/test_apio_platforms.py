"""
Tests of apio_platforms.py
"""

from apio.utils import apio_platforms


def test_platforms():
    """Sanity check the platforms list"""

    # -- Get the (private) platform definitions list
    # platforms_list = apio_platforms._APIO_PLATFORMS_LIST

    # -- Get the dict of ApioPlatform
    platforms_dict = apio_platforms.get_all_apio_platforms()

    # -- Sanity check, sizes should be the same.
    # assert len(platforms_list) == len(platforms_dict)

    # -- Verify that the keys match the ids.
    for platform_id, platform in platforms_dict.items():

        # -- The key should match the object's id field.
        assert platform_id == platform.id

        # -- NOTE: Additional assertions are implemented in the ApioPlatform
        # -- class itself.
