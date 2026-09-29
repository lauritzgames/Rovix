TEMPLATE = {
    "name": "Support",
    "roles": [
        {"id": "staff", "name": "Staff", "color": 3447003, "permissions": ["manage_messages", "manage_channels"], "mentionable": True},
        {"id": "support", "name": "Support", "color": 3066993, "permissions": ["manage_messages", "manage_channels"], "mentionable": True},
        {"id": "developer", "name": "Developer", "color": 10181046, "mentionable": True},
    ],
    "categories": [
        {"id": "information", "name": "📌 INFORMATION", "channels": [
            {"id": "welcome", "name": "👋welcome", "type": "text", "topic": "Support center information.", "messages": ["👋 Welcome to support. Read <#-(:faq:)-> before opening -(;tickets;)-."]},
            {"id": "faq", "name": "📚faq", "type": "text", "messages": ["📚 Frequently asked questions and answers."]},
            {"id": "status", "name": "📡status", "type": "text", "permissions": {"public": {"view_channel": True, "send_messages": False}, "support": {"view_channel": True, "send_messages": True}}, "messages": ["📡 Service status and support updates."]},
        ]},
        {"id": "tickets", "name": "🆘 SUPPORT TICKETS", "channels": [
            {"id": "ticket-panel", "name": "🎫tickets", "type": "text", "topic": "Use the panel to create a private ticket.", "permissions": {"public": {"view_channel": True, "send_messages": False}, "support": {"view_channel": True, "send_messages": True}}, "messages": ["🎫 Click the button below to open a private ticket. -(^support^)- handles support."], "commands": ["ticket setup -(;tickets;)- -(^support^)-", "ticket panel"]},
            {"id": "help", "name": "❓help", "type": "text", "slowmode_delay": 5, "messages": ["❓ General support questions."]},
            {"id": "bug-reports", "name": "🐛bug-reports", "type": "forum", "messages": ["Create detailed bug reports here."]},
            {"id": "status-stage", "name": "🎙️support-stage", "type": "stage"},
        ]},
        {"id": "staff-area", "name": "🔒 STAFF", "permissions": {"public": {"view_channel": False}, "support": {"view_channel": True}, "staff": {"view_channel": True}}, "channels": [
            {"id": "staff-chat", "name": "💬staff-chat", "type": "text", "permissions": "private", "messages": ["🔒 Internal support discussion."]},
            {"id": "mod-logs", "name": "📜mod-logs", "type": "text", "permissions": "private"},
            {"id": "developer-chat", "name": "💻developer-chat", "type": "text", "permissions": {"public": {"view_channel": False}, "developer": {"view_channel": True, "send_messages": True}}},
        ]},
    ],
}
