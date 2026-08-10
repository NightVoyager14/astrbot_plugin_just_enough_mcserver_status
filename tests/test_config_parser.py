import json
import unittest

from src.config import PluginConfig, QuickPingConfig, PingIndicatorConfig
import src.exceptions

ORIGINAL_TEST_CONFIG = """{
    "general": {
        "is_info_card_enabled": true,
        "is_info_text_enabled": true
    },
    "quick_ping": {
        "servers": [
            {
                "__template_key": "server",
                "quick_name": "server",
                "address": "mc.hypixel.net",
                "display_name": "Hypixel",
                "is_bedrock": false,
                "is_default": true
            }
        ]
    },
    "text_info": {
        "is_markdown_enabled": true
    },
    "info_card": {
        "ping_indicator": {
            "is_enabled": true,
            "ping_thresholds": {
                "excellent": 50,
                "good": 100,
                "medium": 200,
                "bad": 500
            }
        },
        "icon": {
            "is_enabled": true
        },
        "title": {
            "is_enabled": true
        },
        "motd": {
            "is_enabled": true,
            "leading": 10
        },
        "player_count": {
            "is_enabled": true
        },
        "background": {
            "is_custom_enabled": false,
            "upload": []
        }
    }
}
"""

EXPECTED_CONFIG_OUTPUT = {
    "general": {
        "is_info_card_enabled": True,
        "is_info_text_enabled": True,
    },
    "quick_ping": {
        "servers": [
            {
                "quick_name": "server",
                "address": "mc.hypixel.net",
                "display_name": "Hypixel",
                "is_bedrock": False,
                "is_default": True,
            }
        ]
    },
    "text_info": {
        "is_markdown_enabled": True,
    },
    "info_card": {
        "ping_indicator": {
            "is_enabled": True,
            "ping_thresholds": {
                "excellent": 50,
                "good": 100,
                "medium": 200,
                "bad": 500,
            },
        },
        "icon": {
            "is_enabled": True,
        },
        "title": {
            "is_enabled": True,
        },
        "motd": {
            "is_enabled": True,
            "leading": 10,
        },
        "player_count": {
            "is_enabled": True,
        },
        "background": {
            "is_custom_enabled": False,
            "upload": [],
        },
    },
}

DUPLIATED_SERVER_CONFIG = """{
    "servers": [
        {
            "__template_key": "server",
            "quick_name": "server",
            "address": "exmaple.jemss",
            "display_name": "JEMSSTestExample",
            "is_bedrock": false,
            "is_default": true
        },
        {
            "__template_key": "server",
            "quick_name": "server",
            "address": "example.jemss",
            "display_name": "JEMSSTestExample",
            "is_bedrock": false,
            "is_default": false
        }
    ]
}
"""

DUPLIATED_DEFAULT_SERVER_CONFIG = """{
    "servers": [
        {
            "__template_key": "server",
            "quick_name": "server",
            "address": "exmaple.jemss",
            "display_name": "JEMSSTestExample",
            "is_bedrock": false,
            "is_default": true
        },
        {
            "__template_key": "server",
            "quick_name": "YuruCampserver",
            "address": "example.jemss",
            "display_name": "JEMSSTestExample",
            "is_bedrock": false,
            "is_default": true
        }
    ]
}
"""

INVALIDATED_PING_THRESHOLD_ORDER_CONFIG = """{
    "is_enabled": true,
    "ping_thresholds": {
        "excellent": 50,
        "good": 20,
        "medium": -100,
        "bad": 50
    }
}

"""


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_config = json.loads(ORIGINAL_TEST_CONFIG)
        self.test_duplicated_server_config = json.loads(DUPLIATED_SERVER_CONFIG)
        self.test_duplicated_default_server_config = json.loads(
            DUPLIATED_DEFAULT_SERVER_CONFIG
        )
        self.test_invalidated_ping_threshold_order_config = json.loads(
            INVALIDATED_PING_THRESHOLD_ORDER_CONFIG
        )

    def test_loading_and_validating_full_config(self):
        verified_test_config = PluginConfig.model_validate(self.test_config)
        self.assertEqual(verified_test_config.model_dump(), EXPECTED_CONFIG_OUTPUT)

    def test_duplicated_server_quick_name_raises_config_exception(self):
        with self.assertRaises(src.exceptions.ConfigException) as ctx:
            QuickPingConfig.model_validate(self.test_duplicated_server_config)
        self.assertEqual(
            ctx.exception.code, src.exceptions.PluginErrorCode.CFG_DUPLICATE_QUICK_NAME
        )
        self.assertRegex(
            ctx.exception.message,
            r"Duplicate quick_name '.*' in config quick_ping.servers\.",
        )

    def test_duplicated_default_server_raises_config_exception(self):
        with self.assertRaises(src.exceptions.ConfigException) as ctx:
            QuickPingConfig.model_validate(self.test_duplicated_default_server_config)
        self.assertEqual(
            ctx.exception.code,
            src.exceptions.PluginErrorCode.CFG_DUPLICATE_DEFAULT_SERVER,
        )
        self.assertRegex(
            ctx.exception.message,
            r"Duplicate default server '.*' in config quick_ping.servers\.",
        )

    def test_invalidated_ping_threshold_order_raises_config_exception(self):
        with self.assertRaises(src.exceptions.ConfigException) as ctx:
            PingIndicatorConfig.model_validate(
                self.test_invalidated_ping_threshold_order_config
            )
        self.assertEqual(
            ctx.exception.code,
            src.exceptions.PluginErrorCode.CFG_INVALID_PING_THRESHOLDS,
        )
        self.assertEqual(
            ctx.exception.message,
            "Config item ping_indicator's ping_thresholds has wrong order.The order must be excellent < good < medium < bad.",
        )


if __name__ == "__main__":
    unittest.main()
