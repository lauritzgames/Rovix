TEMPLATE = {
    "name": "Study",
    "roles": [
        {"id": "staff", "name": "Staff", "color": 3447003, "permissions": ["manage_messages", "manage_channels"], "mentionable": True},
        {"id": "support", "name": "Support", "color": 3066993, "mentionable": True},
        {"id": "teacher", "name": "Teacher", "color": 15844367, "permissions": ["manage_messages"], "hoist": True, "mentionable": True},
    ],
    "categories": [
        {"id": "information", "name": "📚 INFORMATION", "channels": [
            {"id": "welcome", "name": "👋welcome", "type": "text", "topic": "Study server information.", "messages": ["📚 Welcome! Read <#-(:rules:)-> and use -(;tickets;)- for support."]},
            {"id": "rules", "name": "📜rules", "type": "text", "messages": ["📜 Stay respectful and help each other learn."]},
            {"id": "announcements", "name": "📢announcements", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "teacher": {"view_channel": True, "send_messages": True}}, "messages": ["📢 Teacher announcements."]},
        ]},
        {"id": "study", "name": "🧠 STUDY", "channels": [
            {"id": "general", "name": "💬general", "type": "text", "slowmode_delay": 2, "messages": ["🧠 General study chat."]},
            {"id": "homework", "name": "📝homework", "type": "text", "slowmode_delay": 5, "messages": ["📝 Ask homework questions here."]},
            {"id": "resources", "name": "📚resources", "type": "forum", "messages": ["Share useful study resources."]},
            {"id": "questions", "name": "❓questions", "type": "text", "messages": ["❓ Ask a study question."]},
        ]},
        {"id": "rooms", "name": "🔊 STUDY ROOMS", "channels": [
            {"id": "study-1", "name": "🔊Study Room 1", "type": "voice", "user_limit": 10, "bitrate": 64000, "rtc_region": "europe"},
            {"id": "study-2", "name": "🔊Study Room 2", "type": "voice", "user_limit": 10, "bitrate": 64000, "rtc_region": "europe"},
            {"id": "study-stage", "name": "🎙️Study Session", "type": "stage"},
        ]},
        {"id": "tickets", "name": "🆘 SUPPORT", "channels": [
            {"id": "ticket-panel", "name": "🎫tickets", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "support": {"view_channel": True, "send_messages": True}}, "messages": ["🎫 Need help with the server? Open a private ticket."], "commands": ["ticket setup -(;tickets;)- -(^support^)-", "ticket panel"]},
            {"id": "reports", "name": "🐛reports", "type": "forum", "messages": ["Report study-server problems here."]},
        ]},
        {"id": "staff-area", "name": "🔒 STAFF", "permissions": {"public": {"view_channel": False}, "staff": {"view_channel": True}}, "channels": [
            {"id": "staff-chat", "name": "💬staff-chat", "type": "text", "permissions": "private"},
            {"id": "teacher-chat", "name": "👨‍🏫teacher-chat", "type": "text", "permissions": {"public": {"view_channel": False}, "teacher": {"view_channel": True, "send_messages": True}}},
        ]},
    ],
}
