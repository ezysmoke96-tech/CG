# CG Discord Bot

A feature-rich Discord bot for Coruscant Guard operations.

## Railway Deployment

1. Upload this archive to Railway as a new project (or connect via GitHub)
2. Add the following environment variables in Railway → your project → Variables:

| Variable | Required | Description |
|---|---|---|
| `DISCORD_TOKEN` | ✅ | Your bot token from the Discord Developer Portal |
| `GUILD_ID` | ✅ | Your Discord server ID (right-click server → Copy Server ID) |
| `ROBLOX_COOKIE` | ✅ | Your `.ROBLOSECURITY` Roblox cookie |
| `ROBLOX_MAIN_GROUP_ID` | ✅ | Numeric ID of your main Roblox group |
| `ROBLOX_ALLIED_GROUP_IDS` | Recommended | Comma-separated IDs of allied groups |
| `ROBLOX_ENEMY_GROUP_IDS` | Recommended | Comma-separated IDs of enemy groups |

3. Railway will auto-detect `railway.json` and use `python main.py` as the start command.
4. Make sure the service type is set to **Worker** (not Web Service) in Railway.
5. Deploy!

## First Run

After the bot comes online, use `/setup` in your server (Administrator only) to configure:
- Welcome channel (for the join message)
- Moderation Log, Chat Log, Event Log, and CG Comms channels
- Medals

## Commands

| Command | Description |
|---|---|
| `/ping` | Check bot latency |
| `/help` | Show all commands |
| `/setup` | Configure the bot |
| `/editsetup` | Edit configuration |
| `/medals` | View all medals |
| `/assignmedal` | Award a medal |
| `/host` | Log an event |
| `/aos` | Place AOS in CG Comms |
| `/groupsync` | Sync Roblox group rank |
| `/rankcheck` | Check Roblox rank |
| `/bgcheck` | Full Roblox background check (main group + allies + enemies) |
| `/strike` | Issue a strike |
| `/purge` `/kick` `/ban` `/mute` | Moderation |
| `/blacklist` `/unblacklist` | Blacklist management |
| `/announce` `/lockdown` `/unlockdown` | Server management |
| `/roll` `/coinflip` `/8ball` `/rate` `/ship` | Fun |
| `/roast` `/compliment` `/meme` `/joke` `/choose` | More fun |
| `/order66` `/hellothere` `/rogerroger` + more | Star Wars memes |

## Notes

- Data (medals, strikes, AOS, etc.) is stored in local JSON files inside the container.
  On Railway, this resets on each redeploy. Add a Railway PostgreSQL add-on if you need persistent data.
- The welcome message fires automatically when a new member joins the channel set via `/setup`.
