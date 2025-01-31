"""
Generic utilities functions
"""

import uuid


def is_valid_uuid(uuid_to_test: str, version: int = 4) -> bool:
    try:
        # check for validity of Uuid
        uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    except AttributeError as ex:
        print(str(ex))
        print(uuid_to_test)
        raise RuntimeError from ex
    return True
