import json
import unittest
from copy import deepcopy

from src.config import build_config_with_fallback
from src.exceptions import PluginErrorCode

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
                "is_default": true,
                "is_bedrock": false,
                "address": "jemss.test",
                "display_name": "JEMSSTest"
            },
            {
                "__template_key": "server",
                "quick_name": "server2",
                "is_default": false,
                "is_bedrock": false,
                "address": "jemss.test",
                "display_name": "JEMSSTest"
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
                "excellent": 10,
                "good": 100,
                "medium": 2000,
                "bad": 10000
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
        "timestamp": {
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
                "quick_name": "server",  # 这里在写测试用例的expexted output时一定注意不要带上框架注入的__template_key
                "is_default": True,
                "is_bedrock": False,
                "address": "jemss.test",
                "display_name": "JEMSSTest",
            },
            {
                "quick_name": "server2",
                "is_default": False,
                "is_bedrock": False,
                "address": "jemss.test",
                "display_name": "JEMSSTest",
            },
        ]
    },
    "text_info": {
        "is_markdown_enabled": True,
    },
    "info_card": {
        "ping_indicator": {
            "is_enabled": True,
            "ping_thresholds": {
                "excellent": 10,
                "good": 100,
                "medium": 2000,
                "bad": 10000,
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
        "timestamp": {
            "is_enabled": True,
        },
        "background": {
            "is_custom_enabled": False,
            "upload": [],
        },
    },
}


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_config = json.loads(ORIGINAL_TEST_CONFIG)

    # 验证合法配置导入
    def test_loading_and_validating_full_config(self):
        verified_config, notes = build_config_with_fallback(self.test_config)
        self.assertEqual(verified_config.model_dump(), EXPECTED_CONFIG_OUTPUT)
        self.assertEqual(notes, [])

    def test_duplicated_quick_name_keeps_first_occurrence(self):
        config = deepcopy(self.test_config)
        expected_config = deepcopy(EXPECTED_CONFIG_OUTPUT)
        bad_servers = [
            {
                "__template_key": "server",
                "quick_name": "YurucampServer",
                "is_default": False,
                "is_bedrock": False,
                "address": "jemss.yurucamp.test",
                "display_name": "YuruCamp1",
            },
            {
                "__template_key": "server",
                "quick_name": "YurucampServer",
                "is_default": False,
                "is_bedrock": False,
                "address": "jemss.yurucamp.test",
                "display_name": "YuruCamp2",
            },
        ]
        expected_servers = [
            {
                "quick_name": "YurucampServer",
                "is_default": False,
                "is_bedrock": False,
                "address": "jemss.yurucamp.test",
                "display_name": "YuruCamp1",
            }
        ]
        config["quick_ping"]["servers"].extend(bad_servers)
        expected_config["quick_ping"]["servers"].extend(expected_servers)
        verified_config, notes = build_config_with_fallback(config)
        self.assertEqual(verified_config.model_dump(), expected_config)
        self.assertNotEqual(notes, [])
        for note in notes:
            self.assertRegex(
                note,
                r"Duplicate quick_name '.*' in config quick_ping.servers\.",
            )

    def test_duplicated_default_server_resets_extra(self):
        config = deepcopy(self.test_config)
        expected_config = deepcopy(EXPECTED_CONFIG_OUTPUT)
        bad_servers = [
            {
                "__template_key": "server",
                "quick_name": "YurucampServer",
                "is_default": True,
                "is_bedrock": False,
                "address": "jemss.yurucamp.test",
                "display_name": "YuruCamp",
            },
            {
                "__template_key": "server",
                "quick_name": "NotYurucampServer",
                "is_default": True,
                "is_bedrock": False,
                "address": "jemss.yurucamp.test",
                "display_name": "NotYuruCamp",
            },
        ]
        expected_servers = [
            {
                "quick_name": "YurucampServer",
                "is_default": False,
                "is_bedrock": False,
                "address": "jemss.yurucamp.test",
                "display_name": "YuruCamp",
            },
            {
                "quick_name": "NotYurucampServer",
                "is_default": False,
                "is_bedrock": False,
                "address": "jemss.yurucamp.test",
                "display_name": "NotYuruCamp",
            },
        ]
        config["quick_ping"]["servers"].extend(bad_servers)
        expected_config["quick_ping"]["servers"].extend(expected_servers)
        verified_config, notes = build_config_with_fallback(config)
        self.assertEqual(verified_config.model_dump(), expected_config)
        self.assertNotEqual(notes, [])
        for note in notes:
            self.assertRegex(
                note, r"Duplicate default server '.*' in config quick_ping.servers\."
            )

    def test_duplicated_quick_name_and_default_server_both_resolved(self):
        config = deepcopy(self.test_config)
        expected_config = deepcopy(EXPECTED_CONFIG_OUTPUT)
        bad_servers = [
            {
                "__template_key": "server",
                "quick_name": "ServerA",
                "is_default": True,
                "is_bedrock": False,
                "address": "jemss.test",
                "display_name": "JEMSSTest",
            },
            {
                "__template_key": "server",
                "quick_name": "ServerA",
                "is_default": True,
                "is_bedrock": False,
                "address": "jemss.test",
                "display_name": "JEMSSTest",
            },
            {
                "__template_key": "server",
                "quick_name": "NotServer",
                "is_default": True,
                "is_bedrock": False,
                "address": "jemss.test",
                "display_name": "JEMSSTest",
            },
            {
                "__template_key": "server",
                "quick_name": "NotServer",
                "is_default": False,
                "is_bedrock": False,
                "address": "jemss.test",
                "display_name": "JEMSSTest",
            }
        ]
        expected_servers = [
            {
                "quick_name": "ServerA",
                "is_default": True,
                "is_bedrock": False,
                "address": "jemss.test",
                "display_name": "JEMSSTest",
            },
            {
                "quick_name": "NotServer",
                "is_default": False,
                "is_bedrock": False,
                "address": "jemss.test",
                "display_name": "JEMSSTest",
            },
        ]
        config["quick_ping"]["servers"].extend(bad_servers)
        config["quick_ping"]["servers"][0]["is_default"] = False
        expected_config["quick_ping"]["servers"].extend(expected_servers)
        expected_config["quick_ping"]["servers"][0]["is_default"] = False
        verified_config, notes = build_config_with_fallback(config)
        self.assertEqual(verified_config.model_dump(), expected_config)
        self.assertNotEqual(notes, [])
        self.assertTrue(notes[0].startswith("[CFG003]"))
        self.assertTrue(notes[1].startswith("[CFG004]"))

    def test_invalidated_ping_threshold_order_falls_back(self):
        config = deepcopy(self.test_config)
        expected_config = deepcopy(EXPECTED_CONFIG_OUTPUT)
        config["info_card"]["ping_indicator"]["ping_thresholds"] = {
            "excellent": -10,
            "good": 2000,
            "medium": 0,
            "bad": 2,
        }
        expected_config["info_card"]["ping_indicator"]["ping_thresholds"] = {
            "excellent": 50,
            "good": 100,
            "medium": 200,
            "bad": 500,
        }
        verified_config, notes = build_config_with_fallback(config)
        self.assertEqual(verified_config.model_dump(), expected_config)
        self.assertNotEqual(notes, [])
        for note in notes:
            self.assertRegex(
                note,
                r"Config item ping_indicator's ping_thresholds has wrong order.The order must be excellent < good < medium < bad\.",
            )

    def test_invalidated_field_resets(self):
        config = deepcopy(self.test_config)
        expected_config = deepcopy(EXPECTED_CONFIG_OUTPUT)
        config["info_card"]["motd"]["leading"] = "I'm valid leading. Please trust me."
        config["info_card"]["timestamp"]["is_enabled"] = 19690721
        expected_config["info_card"]["motd"]["leading"] = 10
        expected_config["info_card"]["timestamp"]["is_enabled"] = True
        verified_config, notes = build_config_with_fallback(config)
        self.assertEqual(verified_config.model_dump(), expected_config)
        self.assertGreaterEqual(len(notes), 2)
        for note in notes:
            self.assertIn(f"{PluginErrorCode.CFG_VALIDATION_ERROR}", note)
            self.assertIn("type", note)

    def test_invalidated_list_resets(self):
        config = deepcopy(self.test_config)
        expected_config = deepcopy(EXPECTED_CONFIG_OUTPUT)
        bad_servers = [
            {
                "__template_key": "server",
                "quick_name": "DFHServer1",
                "is_default": False,
                "is_bedrock": False,
                "address": 19700424,
                "display_name": "DFH",
            },
            {
                "__template_key": "server",
                "quick_name": "DFHServer2",
                "is_default": "I'm False",
                "is_bedrock": False,
                "address": "can.you.hear.me",
                "display_name": "DFH",
            },
        ]
        expected_servers = []
        config["quick_ping"]["servers"].extend(bad_servers)
        expected_config["quick_ping"]["servers"].extend(expected_servers)
        verified_config, notes = build_config_with_fallback(config)
        self.assertEqual(verified_config.model_dump(), expected_config)
        self.assertNotEqual(notes, [])
        for note in notes:
            self.assertIn(f"{PluginErrorCode.CFG_VALIDATION_ERROR}", note)
            self.assertIn("Config location", note)

    def test_original_config_not_mutated(self):
        config = deepcopy(self.test_config)
        config["quick_ping"]["servers"][1]["quick_name"] = "server"   # 制造重名
        snapshot = deepcopy(config)
        build_config_with_fallback(config)
        self.assertEqual(config, snapshot)
