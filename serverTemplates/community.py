TEMPLATE = {

    "name": "Community",

    "categories": [

        {
            "name": "❗IMPORTANT❗",
            "channels": [

                {
                    "id": "welcome",
                    "name": "👋welcome",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "👋 Welcome to the server!",
                        "Please read <#-(:rules:)-> before chatting."
                    ],
                },

                {
                    "id": "rules",
                    "name": "📜rules",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "📜 Server Rules\n\n"
                        "1. Be respectful.\n"
                        "2. No spam.\n"
                        "3. No harassment.\n"
                        "4. Keep content appropriate.\n"
                        "5. Follow Discord's Terms of Service.\n"
                        "6. Follow staff instructions."
                    ],
                },

                {
                    "id": "announcements",
                    "name": "📣announcements",
                    "type": "text",
                    "permissions": {
                        "public": {
                            "send_messages": False,
                            "view_channel": True,
                        },
                        "staff": {
                            "send_messages": True,
                            "view_channel": True,
                        },
                    },
                    "messages": [
                        "📣 Welcome to the announcements channel!"
                    ],
                },

                {
                    "id": "server-info",
                    "name": "📖server-info",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "📖 Server Information\n\n"
                        "Welcome to our community!"
                    ],
                },

                {
                    "id": "updates",
                    "name": "📰updates",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

            ],
        },

        {
            "name": "💬 COMMUNITY 💬",
            "channels": [

                {
                    "id": "general",
                    "name": "💬general",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "introductions",
                    "name": "👋introductions",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "👋 Introduce yourself to the community!"
                    ],
                },

                {
                    "id": "random",
                    "name": "💭random",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "memes",
                    "name": "😂memes",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "suggestions",
                    "name": "💡suggestions",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "polls",
                    "name": "📊polls",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

            ],
        },

        {
            "name": "📸 MEDIA 📸",
            "channels": [

                {
                    "id": "media",
                    "name": "📷media",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "art",
                    "name": "🎨art",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "videos",
                    "name": "🎬videos",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "screenshots",
                    "name": "📸screenshots",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "music",
                    "name": "🎵music",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

            ],
        },

        {
            "name": "🎮 GAMING 🎮",
            "channels": [

                {
                    "id": "gaming",
                    "name": "🎮gaming",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "game-chat",
                    "name": "🕹️game-chat",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "achievements",
                    "name": "🏆achievements",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "looking-for-group",
                    "name": "🔎looking-for-group",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "gaming-events",
                    "name": "📅gaming-events",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

            ],
        },

        {
            "name": "🤖 BOTS 🤖",
            "channels": [

                {
                    "id": "bot-commands",
                    "name": "🤖bot-commands",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "🤖 Use bot commands in this channel."
                    ],
                },

                {
                    "id": "bot-games",
                    "name": "🎰bot-games",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "bot-stats",
                    "name": "📊bot-stats",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

            ],
        },

        {
            "name": "🎉 EVENTS 🎉",
            "channels": [

                {
                    "id": "events",
                    "name": "📅events",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "competitions",
                    "name": "🏆competitions",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "giveaways",
                    "name": "🎁giveaways",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "event-chat",
                    "name": "🗓️event-chat",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

            ],
        },

        {
            "name": "🆘 SUPPORT 🆘",
            "channels": [

                {
                    "id": "help",
                    "name": "❓help",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "bug-reports",
                    "name": "🐛bug-reports",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "feature-requests",
                    "name": "💡feature-requests",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "tickets",
                    "name": "🎫tickets",
                    "type": "text",
                    "permissions": "private",
                    "messages": [
                        "🎫 Create a ticket if you need help."
                    ],
                },

            ],
        },

        {
            "name": "🔊 VOICE 🔊",
            "channels": [

                {
                    "id": "general-voice",
                    "name": "🔊General",
                    "type": "voice",
                    "permissions": "public",
                },

                {
                    "id": "gaming-1",
                    "name": "🔊Gaming 1",
                    "type": "voice",
                    "permissions": "public",
                },

                {
                    "id": "gaming-2",
                    "name": "🔊Gaming 2",
                    "type": "voice",
                    "permissions": "public",
                },

                {
                    "id": "chill",
                    "name": "🔊Chill",
                    "type": "voice",
                    "permissions": "public",
                },

                {
                    "id": "music-voice",
                    "name": "🔊Music",
                    "type": "voice",
                    "permissions": "public",
                },

                {
                    "id": "event-vc",
                    "name": "🔊Event VC",
                    "type": "voice",
                    "permissions": "public",
                },

            ],
        },

        {
            "name": "🔒 STAFF 🔒",
            "channels": [

                {
                    "id": "staff-chat",
                    "name": "💬staff-chat",
                    "type": "text",
                    "permissions": "private",
                    "messages": [],
                },

                {
                    "id": "staff-info",
                    "name": "📋staff-info",
                    "type": "text",
                    "permissions": "private",
                    "messages": [],
                },

                {
                    "id": "mod-logs",
                    "name": "📜mod-logs",
                    "type": "text",
                    "permissions": "private",
                    "messages": [],
                },

                {
                    "id": "reports",
                    "name": "⚠️reports",
                    "type": "text",
                    "permissions": "private",
                    "messages": [],
                },

            ],
        },

    ],

}