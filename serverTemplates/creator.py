TEMPLATE = {
    "name": "Creator",
    "roles": [
        {"id": "staff", "name": "Staff", "color": 3447003, "permissions": ["manage_messages", "manage_channels"], "mentionable": True},
        {"id": "support", "name": "Support", "color": 3066993, "mentionable": True},
        {"id": "creator", "name": "Creator", "color": 10181046, "hoist": True, "mentionable": True},
    ],
    "categories": [
        {"id": "creator", "name": "📢 CREATOR", "channels": [
            {"id": "welcome", "name": "👋welcome", "type": "text", "topic": "Creator community information.", "messages": ["🎥 Welcome! Read <#-(:rules:)-> and use -(;tickets;)- for support."]},
            {"id": "announcements", "name": "📣announcements", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "creator": {"view_channel": True, "send_messages": True}}, "messages": ["📣 Creator announcements."]},
            {"id": "updates", "name": "📰updates", "type": "text", "messages": []},
            {"id": "rules", "name": "📜rules", "type": "text", "messages": ["📜 Keep content respectful and creator-focused."]},
        ]},
        {"id": "community", "name": "💬 COMMUNITY", "channels": [
            {"id": "general", "name": "💬general", "type": "text", "slowmode_delay": 2, "messages": ["💬 Community chat."]},
            {"id": "showcase", "name": "🎨showcase", "type": "text", "messages": ["🎨 Show your work."]},
            {"id": "feedback", "name": "💡feedback", "type": "forum", "messages": ["Create a feedback post."]},
            {"id": "media", "name": "📷media", "type": "text", "nsfw": False, "messages": []},
        ]},
        {"id": "voice", "name": "🔊 VOICE", "channels": [
            {"id": "creator-vc", "name": "🔊Creator Room", "type": "voice", "user_limit": 10, "bitrate": 96000, "rtc_region": "europe"},
            {"id": "collab-vc", "name": "🔊Collab Room", "type": "voice", "user_limit": 0, "rtc_region": "europe"},
        ]},
        {"id": "tickets", "name": "🆘 SUPPORT", "channels": [
            {"id": "ticket-panel", "name": "🎫tickets", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "support": {"view_channel": True, "send_messages": True}}, "messages": ["🎫 Creator support starts here."], "commands": ["ticket setup -(;tickets;)- -(^support^)-", "ticket panel"]},
            {"id": "reports", "name": "🐛reports", "type": "forum", "messages": ["Report creator issues here."]},
        ]},
        {"id": "staff-area", "name": "🔒 STAFF", "permissions": {"public": {"view_channel": False}, "staff": {"view_channel": True}}, "channels": [
            {"id": "staff-chat", "name": "💬staff-chat", "type": "text", "permissions": "private"},
            {"id": "creator-logs", "name": "📜creator-logs", "type": "text", "permissions": "private"},
        ]},
    ],
}
