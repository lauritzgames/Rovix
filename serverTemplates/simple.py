TEMPLATE = {
    "name": "Simple",
    "roles": [
        {"id": "staff", "name": "Staff", "color": 3447003, "permissions": ["manage_messages", "manage_channels"], "mentionable": True},
        {"id": "support", "name": "Support", "color": 3066993, "mentionable": True},
    ],
    "categories": [
        {"id": "info", "name": "❗ IMPORTANT", "channels": [
            {"id": "welcome", "name": "👋welcome", "type": "text", "topic": "Welcome to the server.", "messages": ["👋 Welcome! Read <#-(:rules:)-> and contact -(;tickets;)- if you need help."]},
            {"id": "rules", "name": "📜rules", "type": "text", "permissions": "public", "messages": ["📜 Be respectful, do not spam, follow Discord rules, and listen to staff."]},
            {"id": "announcements", "name": "📣announcements", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "staff": {"view_channel": True, "send_messages": True}}, "messages": ["📣 Server announcements go here."]},
        ]},
        {"id": "community", "name": "💬 COMMUNITY", "channels": [
            {"id": "general", "name": "💬general", "type": "text", "slowmode_delay": 2, "messages": ["💬 Welcome to -(;community;)-!"]},
            {"id": "media", "name": "📷media", "type": "text", "nsfw": False, "messages": ["📷 Share your media here."]},
            {"id": "stage", "name": "🎙️stage", "type": "stage", "permissions": "public"},
            {"id": "voice", "name": "🔊General", "type": "voice", "user_limit": 10, "bitrate": 64000, "rtc_region": "europe"},
        ]},
        {"id": "tickets", "name": "🆘 SUPPORT", "channels": [
            {"id": "ticket-panel", "name": "🎫tickets", "type": "text", "topic": "Private support tickets.", "permissions": {"public": {"view_channel": True, "send_messages": False}, "support": {"view_channel": True, "send_messages": True}}, "messages": ["🎫 Need help? Use the ticket panel below. -(^support^)- can assist you."], "commands": ["ticket setup -(;tickets;)- -(^support^)-", "ticket panel"]},
            {"id": "support-forum", "name": "🐛bug-reports", "type": "forum", "messages": ["Post bugs with steps to reproduce them."]},
        ]},
        {"id": "staff-area", "name": "🔒 STAFF", "permissions": {"public": {"view_channel": False}, "staff": {"view_channel": True}}, "channels": [
            {"id": "staff-chat", "name": "💬staff-chat", "type": "text", "permissions": "private", "messages": ["🔒 Staff area."]},
            {"id": "logs", "name": "📜logs", "type": "text", "permissions": "private"},
        ]},
    ],
}
