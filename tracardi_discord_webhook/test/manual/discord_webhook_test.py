import asyncio
from tracardi_discord_webhook.plugin import DiscordWebHookAction



async def main():
    init = {
        "url": "https://discord.com/api/webhooks/879106873004032030/kXYSPpIdV0nHCAdd9d5kh3ee1TYO6nUsU5am70hCV7fWWkUZWuE3jIocT2FpnxKuYc1R"
    }

    plugin = DiscordWebHookAction(**init)

    payload = {
        "content": "send message\nssdasd",
        "username": "risto"
    }

    results = await plugin.run(payload)
    print(results)


asyncio.run(main())
