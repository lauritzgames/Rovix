TEMPLATE = {

    "name": "Simple",

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
                        "1. Be respectful to everyone.\n"
                        "2. No spam or flooding.\n"
                        "3. No harassment or hate speech.\n"
                        "4. Keep content appropriate.\n"
                        "5. Follow Discord's Terms of Service.\n"
                        "6. Listen to the staff team."
                    ],
                },

                {
                    "id": "announcements",
                    "name": "📣announcements",
                    "type": "text",
                    "permissions": {
                        "public": {
                            "view_channel": True,
                            "send_messages": False,
                        },
                        "staff": {
                            "view_channel": True,
                            "send_messages": True,
                        },
                    },
                    "messages": [
                        "📣 Server announcements will appear here."
                    ],
                },

                {
                    "id": "server-info",
                    "name": "📖server-info",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "📖 Server Information\n\n"
                        "Welcome to the server!"
                    ],
                },

            ],
        },

        {
            "name": "👥COMMUNITY👥",
            "channels": [

                {
                    "id": "general",
                    "name": "💬general",
                    "type": "text",
                    "permissions": "public",
                    "messages": [],
                },

                {
                    "id": "media",
                    "name": "📷media",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "📷 Share your pictures and media here!"
                    ],
                },

                {
                    "id": "vc-1",
                    "name": "🔊vc-1",
                    "type": "voice",
                    "permissions": "public",
                },

                {
                    "id": "vc-2",
                    "name": "🔊vc-2",
                    "type": "voice",
                    "permissions": "public",
                },

                {
                    "id": "event-vc",
                    "name": "🔊event-vc",
                    "type": "voice",
                    "permissions": "public",
                },

            ],
        },

    ],

}