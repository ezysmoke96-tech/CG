# CG Discord Bot

A feature-rich Discord bot for Coruscant Guard operations.

## Railway Deployment

1. Upload this archive to Railway as a new project (or connect via GitHub)
2. Add the following environment variables in Railway → your project → Variables:

| Variable | Required | Description |
|---|---|---|
| `DISCORD_TOKEN` | Yes | Your bot token from the Discord Developer Portal |
| `GUILD_ID` | Yes | Your Discord server ID (right-click server → Copy Server ID) |
| `ROBLOX_COOKIE` | Yes | Your `.ROBLOSECURITY` Roblox cookie |
| `ROBLOX_MAIN_GROUP_ID` | Yes | Numeric ID of your main Roblox group |
| `ROBLOX_ALLIED_GROUP_IDS` | Recommended | Comma-separated IDs of allied groups |
| `ROBLOX_ENEMY_GROUP_IDS` | Recommended | Comma-separated IDs of enemy groups |

3. Railway auto-detects `railway.json` and runs `python main.py`.
4. Set the service type to **Worker** (not Web Service) in Railway settings.
5. Deploy.

## First Run

After the bot is online, use `/setup` (Administrator only) to configure:
- Welcome channel
- Moderation Log, Chat Log, Event Log, CG Comms channels
- Medals

## Background Check Requirements

`/bgcheck` automatically evaluates users against these minimums:

| Requirement | Minimum |
|---|---|
| Badges | 175 |
| Friends | 20 |
| Following | 10 |
| Account Age | 365 days |

A user must meet **all** requirements to receive a PASS verdict.

## Notes

- Data is stored in local JSON files. It resets on Railway redeploys.
  Add a Railway PostgreSQL add-on for persistent storage.
- For two servers: leave `GUILD_ID` blank so commands sync globally to all servers.
