TEMPLATE = {
    "name": "Gaming",
    "roles": [
        {"id": "staff", "name": "Staff", "color": 3447003, "permissions": ["manage_messages", "manage_channels"], "mentionable": True},
        {"id": "support", "name": "Support", "color": 3066993, "mentionable": True},
        {"id": "gamer", "name": "Gamer", "color": 10181046, "hoist": True},
    ],
    "categories": [
        {"id": "start", "name": "📌 START HERE", "channels": [
            {"id": "welcome", "name": "👋welcome", "type": "text", "topic": "Gaming server information.", "messages": ["🎮 Welcome! Check <#-(:rules:)-> and use -(;tickets;)- for support."]},
            {"id": "rules", "name": "📜rules", "type": "text", "messages": ["📜 Respect players, no spam, cheating, harassment, or malicious links."]},
            {"id": "news", "name": "📣announcements", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "staff": {"view_channel": True, "send_messages": True}}, "messages": ["📣 Gaming news goes here."]},
        ]},
        {"id": "games", "name": "🎮 GAMING", "channels": [
            {"id": "general", "name": "💬general", "type": "text", "slowmode_delay": 2, "messages": ["🎮 Talk about games here."]},
            {"id": "clips", "name": "📸clips", "type": "text", "messages": ["📸 Share your best clips."]},
            {"id": "looking", "name": "🔎looking-for-group", "type": "text", "messages": ["🔎 Find teammates here."]},
            {"id": "game-forum", "name": "🕹️game-discussion", "type": "forum", "messages": ["Create a post for a game or topic."]},
            {"id": "gaming-vc", "name": "🔊Gaming", "type": "voice", "user_limit": 20, "bitrate": 96000, "rtc_region": "europe"},
            {"id": "stage", "name": "🎙️Events", "type": "stage"},
        ]},
        {"id": "tickets", "name": "🆘 SUPPORT", "channels": [
            {"id": "ticket-panel", "name": "🎫tickets", "type": "text", "topic": "Support ticket panel.", "permissions": {"public": {"view_channel": True, "send_messages": False}, "support": {"view_channel": True, "send_messages": True}}, "messages": ["🎫 Open a private support ticket below."], "commands": ["ticket setup -(;tickets;)- -(^support^)-", "ticket panel"]},
            {"id": "reports", "name": "🐛bug-reports", "type": "forum", "messages": ["Use this for public bug reports."]},
        ]},
        {"id": "staff-area", "name": "🔒 STAFF", "permissions": {"public": {"view_channel": False}, "staff": {"view_channel": True}}, "channels": [
            {"id": "staff-chat", "name": "💬staff-chat", "type": "text", "permissions": "private"},
            {"id": "mod-logs", "name": "📜mod-logs", "type": "text", "permissions": "private"},
        ]},
    ],
}
