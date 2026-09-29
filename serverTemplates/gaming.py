TEMPLATE = {

    "name": "Gaming",

    "categories": [

        {
            "name": "🎮 GAMING",
            "channels": [

                {
                    "id": "general",
                    "name": "💬general",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "🎮 Welcome to the gaming community!"
                    ],
                },

                {
                    "id": "game-chat",
                    "name": "🎮game-chat",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "🎮 Talk about your favorite games here!"
                    ],
                },

                {
                    "id": "clips",
                    "name": "📸clips",
                    "type": "text",
                    "permissions": "public",
                    "messages": [
                        "📸 Share your best gaming clips here!"
                    ],
                },

                {
                    "id": "announcements",
                    "name": "📢announcements",
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
                        "📢 Gaming announcements will appear here."
                    ],
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

            ],
        },

    ],

}