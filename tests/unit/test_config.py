from discord_for_chatgpt import config


def test_settings_loaded():
    s = config.settings
    assert hasattr(s, "database_url")
    assert hasattr(s, "discord_client_id")
