"""Base Script for Cortex XSOAR (aka Demisto)

This is an empty script with some basic structure according
to the code conventions.

MAKE SURE YOU REVIEW/REPLACE ALL THE COMMENTS MARKED AS "TODO"

Developer Documentation: https://xsoar.pan.dev/docs/welcome
Code Conventions: https://xsoar.pan.dev/docs/integrations/code-conventions
Linting: https://xsoar.pan.dev/docs/integrations/linting

"""

from typing import Any, Dict

import demistomock as demisto
from CommonServerPython import *
from CommonServerUserPython import *

""" STANDALONE FUNCTION """


# TODO: REMOVE the following dummy function:
def basescript_dummy(dummy: str) -> Dict[str, str]:
    """Returns a simple python dict with the information provided
    in the input (dummy).

    :type dummy: ``str``
    :param dummy: string to add in the dummy dict that is returned

    :return: dict as {"dummy": dummy}
    :rtype: ``str``
    """
    demisto.executeCommand("TestScript3", args={})

    return {"dummy": dummy}


# TODO: ADD HERE THE FUNCTIONS TO INTERACT WITH YOUR PRODUCT API


""" COMMAND FUNCTION """


# TODO: REMOVE the following dummy command function
def basescript_dummy_command(args: Dict[str, Any]) -> CommandResults:
    dummy = args.get("dummy")
    if not dummy:
        raise ValueError("dummy not specified")

    # Call the standalone function and get the raw response
    result = basescript_dummy(dummy)

    return CommandResults(
        outputs_prefix="TestScript4",
        outputs_key_field="",
        outputs=result,
    )


# TODO: ADD additional command functions that translate XSOAR inputs/outputs


""" MAIN FUNCTION """


def main():
    try:
        # TODO: replace the invoked command function with yours
        return_results(basescript_dummy_command(demisto.args()))
    except Exception as ex:
        return_error(f"Failed to execute TestScript4. Error: {ex!s}")


""" ENTRY POINT """


if __name__ in ("__main__", "__builtin__", "builtins"):  # pragma: no cover
    main()
