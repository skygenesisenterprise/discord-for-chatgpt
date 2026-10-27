def test_mcp_tools_registered():
    from discord_for_chatgpt.mcp import server
    # Check that tools are defined
    assert hasattr(server, 'discord_get_identity')
    assert hasattr(server, 'discord_list_guilds')
    assert hasattr(server, 'discord_list_channels')
    assert hasattr(server, 'discord_get_channel')
    assert hasattr(server, 'discord_read_messages')
    assert hasattr(server, 'discord_search_messages')
