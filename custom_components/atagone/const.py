""" Constants for the Atag One Integration """

import logging

_LOGGER = logging.getLogger(__package__)

DOMAIN = "atagone"
DEFAULT_NAME = "Atag One"
DEFAULT_TIMEOUT = 30
BASE_URL = "http://{0}:{1}{2}"
MAC_ADDRESS = "01:23:45:67:89:01"
DEFAULT_MIN_TEMP = 4
DEFAULT_MAX_TEMP = 27

ATAGONE_PLATFORMS = ["climate", "sensor"]


""" jsonPayload data templates
    update payload need to be in exact order. So, using string instead of json.dumps
"""
UPDATE_MODE = """{{
    "update_message":{{
        "seqnr":0,
        "account_auth":{{
            "user_account":"",
            "mac_address":"{0}"
        }},
        "device":null,
        "status":null,
        "report":null,
        "configuration":null,
        "schedules":null,
        "control":{{
            "ch_mode":{1}
        }}
    }}
}}"""

UPDATE_TEMP = """{{
    "update_message":{{
        "seqnr":0,
        "account_auth":{{
            "user_account":"",
            "mac_address":"{0}"
        }},
        "device": null,
        "status": null,
        "report": null,
        "configuration": null,
        "schedules": null,
        "control":{{
            "ch_mode_temp":{1}
        }}
    }}
}}"""

UPDATE_VACATION = """{{
    "update_message":{{
        "seqnr":0,
        "account_auth":{{
            "user_account":"",
            "mac_address":"{0}"
        }},
        "device": null,
        "status": null,
        "report": null,
        "configuration":{{
            "start_vacation":{1},
            "ch_vacation_temp":{2}
        }},
        "schedules": null,
        "control":{{
            "vacation_duration":{3}
        }}
    }}
}}"""

CANCEL_VACATION = """{{
    "update_message":{{
        "seqnr":0,
        "account_auth":{{
            "user_account":"",
            "mac_address":"{0}"
        }},
        "device": null,
        "status": null,
        "report": null,
        "schedules": null,
        "control":{{
            "vacation_duration":0
        }},
        "configuration":{{
            "start_vacation":0
        }}
    }}
}}"""

PAIR_MESSAGE = """{{
    "pair_message":{{
        "seqnr": 0,
        "accounts":{{
            "entries":[{{
                "user_account": "",
                "mac_address": {0},
                "device_name": "Home Assistant",
                "account_type": 0
            }}]
        }}
    }}
}}"""

