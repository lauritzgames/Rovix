import asyncio
import json
import os
import re
import unicodedata
from datetime import datetime, timezone

import discord

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "rovix.json")
DATA_LOCK = asyncio.Lock()
SUBSTITUTIONS = str.maketrans({
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "@": "a",
    "$": "s",
})

def utcnow():
    return datetime.now(timezone.utc)

def normalize_text(value):
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return value.casefold().translate(SUBSTITUTIONS)

def normalize_name(value):
    return re.sub(r"[^a-z0-9]+", "", normalize_text(value))

def default_config():
    return {
        "automod": {
            "words": [],
            "links": True,
            "spam": True,
            "mentions": True,
            "invites": True,
            "caps": True,
            "whitelist": [],
            "max_mentions": 5,
            "spam_window": 8,
            "spam_limit": 6
        },
        "logging": {
            "channel_id": None,
            "events": {
                "messages": True,
                "moderation": True,
                "channels": True,
                "roles": True,
                "members": True,
                "voice": True,
                "server": True
            }
        },
        "tickets": {
            "category_id": None,
            "support_role_id": None
        },
        "member": {
            "welcome_channel_id": None,
            "welcome_message": "Welcome {member} to {server}!",
            "goodbye_channel_id": None,
            "goodbye_message": "{member} has left {server}.",
            "autorole_id": None,
            "verification_role_id": None,
            "report_channel_id": None,
            "feedback_channel_id": None,
            "suggestion_channel_id": None
        },
        "reaction_roles": {},
        "warnings": {}
    }

def load_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}

DATA = load_data()

def guild_config(guild_id):
    key = str(guild_id)
    if key not in DATA:
        DATA[key] = default_config()
    return DATA[key]

async def save_data():
    async with DATA_LOCK:
        os.makedirs(DATA_DIR, exist_ok=True)
        temporary = f"{DATA_FILE}.tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(DATA, file, indent=2, ensure_ascii=False)
        os.replace(temporary, DATA_FILE)

async def send_log(guild, title, description, event="server", colour=None):
    config = guild_config(guild.id)
    if not config["logging"]["events"].get(event, True):
        return
    channel_id = config["logging"].get("channel_id")
    channel = guild.get_channel(channel_id) if channel_id else None
    if not isinstance(channel, discord.TextChannel):
        return
    embed = discord.Embed(
        title=title,
        description=description[:4000],
        colour=colour or discord.Colour.blurple(),
        timestamp=utcnow()
    )
    try:
        await channel.send(embed=embed)
    except discord.HTTPException:
        pass

def ticket_owner_id(channel):
    if not channel.topic:
        return None
    match = re.fullmatch(r"rovix-ticket:(\d+)", channel.topic)
    return int(match.group(1)) if match else None

def find_ticket_for_user(guild, user_id):
    return next((channel for channel in guild.text_channels if ticket_owner_id(channel) == user_id), None)

def safe_channel_name(value):
    value = value.strip().lower().replace(" ", "-")
    value = re.sub(r"[^a-z0-9\-_]", "", value)
    return value[:100] or "channel"

async def create_text_channel(guild, name, category=None, overwrites=None, topic=None):
    kwargs = {
        "name": safe_channel_name(name),
        "category": category,
        "overwrites": overwrites or {}
    }
    if topic is not None:
        kwargs["topic"] = topic
    return await guild.create_text_channel(**kwargs)

async def add_warning(guild_id, user_id, moderator_id, reason):
    config = guild_config(guild_id)
    entries = config["warnings"].setdefault(str(user_id), [])
    entries.append({
        "moderator_id": moderator_id,
        "reason": reason,
        "timestamp": utcnow().isoformat()
    })
    await save_data()
    return len(entries)

async def clear_warnings(guild_id, user_id):
    guild_config(guild_id)["warnings"].pop(str(user_id), None)
    await save_data()

def warning_entries(guild_id, user_id):
    return guild_config(guild_id)["warnings"].setdefault(str(user_id), [])
