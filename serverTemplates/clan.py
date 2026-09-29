TEMPLATE = {
    "name": "Clan",
    "roles": [
        {"id": "staff", "name": "Staff", "color": 3447003, "permissions": ["manage_messages", "manage_channels"], "mentionable": True},
        {"id": "support", "name": "Support", "color": 3066993, "mentionable": True},
        {"id": "member", "name": "Member", "color": 3066993, "hoist": True},
        {"id": "officer", "name": "Officer", "color": 15158332, "permissions": ["manage_messages"], "hoist": True, "mentionable": True},
    ],
    "categories": [
        {"id": "clan", "name": "⚔️ CLAN", "channels": [
            {"id": "welcome", "name": "👋welcome", "type": "text", "topic": "Clan information.", "messages": ["⚔️ Welcome to the clan! Read <#-(:rules:)-> and use -(;tickets;)- for support."]},
            {"id": "rules", "name": "📜rules", "type": "text", "messages": ["📜 Respect clan members and follow officer instructions."]},
            {"id": "announcements", "name": "📣announcements", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "officer": {"view_channel": True, "send_messages": True}}, "messages": ["📣 Officer announcements."]},
        ]},
        {"id": "chat", "name": "💬 CHAT", "channels": [
            {"id": "general", "name": "💬general", "type": "text", "slowmode_delay": 2, "messages": ["💬 Clan chat."]},
            {"id": "strategy", "name": "🧠strategy", "type": "text", "messages": ["🧠 Plan strategies here."]},
            {"id": "media", "name": "📸media", "type": "text", "nsfw": False, "messages": ["📸 Share clan media."]},
            {"id": "discussion", "name": "💬discussion", "type": "forum", "messages": ["Start a clan discussion."]},
        ]},
        {"id": "events", "name": "🏆 EVENTS", "channels": [
            {"id": "events-chat", "name": "📅events", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "officer": {"view_channel": True, "send_messages": True}}, "messages": ["🏆 Clan events are posted here."]},
            {"id": "event-vc", "name": "🔊Event VC", "type": "voice", "user_limit": 20, "bitrate": 96000, "rtc_region": "europe"},
            {"id": "event-stage", "name": "🎙️Clan Events", "type": "stage"},
        ]},
        {"id": "tickets", "name": "🆘 SUPPORT", "channels": [
            {"id": "ticket-panel", "name": "🎫tickets", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "support": {"view_channel": True, "send_messages": True}}, "messages": ["🎫 Open a private support ticket below."], "commands": ["ticket setup -(;tickets;)- -(^support^)-", "ticket panel"]},
            {"id": "reports", "name": "🐛reports", "type": "forum", "messages": ["Report clan issues here."]},
        ]},
        {"id": "officers", "name": "🔒 OFFICERS", "permissions": {"public": {"view_channel": False}, "officer": {"view_channel": True}, "staff": {"view_channel": True}}, "channels": [
            {"id": "officer-chat", "name": "💬officer-chat", "type": "text", "permissions": "private"},
            {"id": "officer-logs", "name": "📜officer-logs", "type": "text", "permissions": "private"},
        ]},
    ],
}
