#ModMail
# Bot's token
token = "ODU5NTg0NjU4Njc2MzgzNzU0.YNu0mA.7sum-f7YP6EFHFG0CnF66gUUrkk"

# Bot Listing Tokens
topgg_token = "" # Top.gg token
dbots_token = "" # Discord Bots token
dbl_token = "" # Discord Bot List token
bod_token = "" # Bots on Discord token
bfd_token = "" # Bots for Discord token
dboats_token = "" # Discord Boats token


sentry_url = "" # Sentry URL

# Whether the bot is for testing, if true, stats and errors will not be posted
testing = True

ipc_channel = "modmail-gof" # PUBSUB channel for Redis

# Postgres database credentials
database = {
    "database": "postgres",
    "user": "postgres",
    "password": "onapostitunderthekeyboard",
    "host": "localhost",
    "port": 5432
}

clusters = 1 # Number of clusters

additional_shards = 1 # Additional shards to launch

default_prefix = "," # The default prefix for commands

# The server to send tickets to, no confirmation messages if set
default_server = 448405740797952010

# Status of the bot
activity = f"DM to open a ticket"

# Whether or not to fetch all members
fetch_all_members = True

# The main bot owner
owner = 365262543872327681

# Bot owners that have access to owner commands
owners = [
    446290930723717120,
    381998065327931392, 
    365262543872327681,
]

# Bot admins that have access to admin commands
admins = [
    446290930723717120,
    381998065327931392,
    365262543872327681,
    448404519790051330,
    791394319075377243, # SparseSpace
    757750333144563724,
]

# Cogs to load on startup
initial_extensions = [
    "cogs.error_handler",
    "cogs.communication",
    "cogs.events",
    "cogs.modmail_channel",
    "cogs.general",
    "cogs.miscellaneous",
    "cogs.info",
    "cogs.direct_message",
    "cogs.moderation",
    "cogs.logs",
    "cogs.configuration",
    "cogs.core",
    "cogs.snippet",
    "cogs.premium",
    "cogs.admin",
    "cogs.owner",
]

# Channels to send logs
join_channel = 816480943228452895
event_channel = 816480957288546314
admin_channel = 816480968830353458
member_channel = 796326430283005982
#counting_channel = 860272912177954816

# This is where patron roles are at
main_server = 607652789304164362

# Patron roles for premium servers
premium1 = 859618384877977601
premium3 = None
premium5 = None

# The colour used in embeds
primary_colour = 0x1E90FF
user_colour = 0x00FF00
mod_colour = 0xFF4500
error_colour = 0xFF0000
booster_colour = 0x9400D3
branding_colour = 0x00bfff

# Level reward roles
rewards = [
    798899285948497950, # Newbie
    798892809863036949, # Apprentice
    798893331663945768, # Sales Operative
    798895195763638303, # Team Leader
    798893533174956042, # VIP
    798893644609224744, # Franchisee
    798893730341453857, # Executive
    798893876404289537, # Director
    798893961313648641, # Millionaire
    798894035182944316, #Multi-Millionaire
]

key_words = [
    "WARN", 
    "MUTE", 
    "UNMUTE", 
    "KICK", 
    "BAN", 
    "UNBAN"
]

default_bad_words = [
    "@everyone",
    "b2b",
    "act2",
]

moderator_permissions = [
    "administrator",
    "manage_guild",
    "manage_messages",
]

# Listing the approved reactions to watch for
star_reactions = [
    "⭐", 
    ":questionable_star:", 
    ":star_struck:", 
    ":star2:", 
    ":StarPiece:", 
    ":purple_star:"
]

role_perms = [
    "administrator", 
    "manage_guild", 
    "manage_webhooks", 
    "manage_channels", 
    "manage_roles", 
    "manage_emojis", 
    "manage_messages", 
    "manage_nicknames", 
    "view_audit_log", 
    "view_guild_insights", 
    "kick_members", 
    "ban_members", 
    "move_members", 
    "deafen_members", 
    "mute_members", 
    "read_messages", 
    "send_messages", 
    "send_tts_messages", 
    "embed_links", 
    "attach_files", 
    "read_message_history", 
    "add_reactions", 
    "external_emojis", 
    "connect", "speak", 
    "priority_speaker", 
    "use_voice_activation", 
    "stream", 
    "create_instant_invite", 
    "change_nickname",
     "mention_everyone"
]
key_perms = [
    "administrator", 
    "manage_guild", 
    "manage_roles", 
    "manage_channels", 
    "manage_messages", 
    "manage_webhooks", 
    "manage_nicknames", 
    "manage_emojis", 
    "kick_members", 
    "mention_everyone"
]




#RaidMode
guildID = 448405740797952010 #Insert the guildID of the server that the bot will be running in here.
StaffRoleID = 826229734601916506 #Change this value to the role in the server that will give bot perms to the anti-raid commands
SystemLogsChannelID = 859852804045406238 #Change this value to where the bot will send all logs of commands too

customfooter = True #Set this the True if you like to have a custom footer at embeds            
customfootvalue = 'Testing the custom Footer'  #Place the text of the custom footers

#Anti-Raid:
GracePeriodForKicks = 600 #Adjust this value for the bot to look for members to kick who joined during a certain amount of time before anti-raid is enabled, default is 10 minutes, seconds only 
IncludeInviteLink = False #Change this to True for Yes, False for No. This allows for a discord invite to be on the message that the bot sends to a member who is kicked due to anti-raid
DiscordServerInviteLink = '' #Place in here the link to the discord. Use https, for example: https://discord.gg/yourvanityurl