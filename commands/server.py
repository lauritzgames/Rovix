import discord


class ServerPanelSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Management", value="management", emoji="🛠️"),
            discord.SelectOption(label="Moderation", value="moderation", emoji="🛡️"),
            discord.SelectOption(label="AutoMod", value="automod", emoji="🤖"),
            discord.SelectOption(label="Tickets", value="tickets", emoji="🎫"),
            discord.SelectOption(label="Logging", value="logging", emoji="📜"),
            discord.SelectOption(label="Member Experience", value="members", emoji="👥"),
            discord.SelectOption(label="Server Utilities", value="utilities", emoji="📊"),
            discord.SelectOption(label="Advanced", value="advanced", emoji="🧠")
        ]
        super().__init__(placeholder="Select a Rovix section", options=options)

    async def callback(self, interaction: discord.Interaction):
        panels = {
            "management": (
                "🛠️ Management",
                "/lock\n/unlock\n/clear\n/hide\n/unhide\n/rename\n/topic\n/movechannel\n/createforum"
            ),
            "moderation": (
                "🛡️ Moderation",
                "/ban\n/unban\n/kick\n/timeout\n/untimeout\n/warn\n/warnings\n/clearwarnings\n/softban\n/nick\n/purge\n/history\n/modlogs"
            ),
            "automod": (
                "🤖 AutoMod",
                "/automod words\n/automod links\n/automod spam\n/automod mentions\n/automod invites\n/automod caps\n/automod settings\n/automod whitelist"
            ),
            "tickets": (
                "🎫 Tickets",
                "/ticket setup\n/ticket create\n/ticket close\n/ticket delete\n/ticket add\n/ticket remove\n/ticket rename\n/ticket transcript\n/ticket settings"
            ),
            "logging": (
                "📜 Logging",
                "/logs setup\n/logs messages\n/logs moderation\n/logs channels\n/logs roles\n/logs members\n/logs voice\n/logs server"
            ),
            "members": (
                "👥 Member Experience",
                "/welcome\n/goodbye\n/autorole\n/verification\n/rules\n/membercount\n/serverstats"
            ),
            "utilities": (
                "📊 Server Utilities",
                "/poll\n/embed\n/announce\n/say\n/remind\n/timer\n/giveaway\n/reactionrole\n/suggest\n/afk\n/8ball\n/choose"
            ),
            "advanced": (
                "🧠 Advanced Rovix",
                "/rovix serveraudit\n/rovix permissionsaudit\n/rovix cleanup\n/rovix duplicatechannels\n/rovix roleaudit\n/rovix channelstats\n/rovix activity\n/rovix whois\n/rovix serverhealth\n/rovix botlist\n/rovix commands\n/rovix help\n/rovix report\n/rovix feedback\n/rovix suggestion"
            )
        }
        title, body = panels[self.values[0]]
        embed = discord.Embed(title=title, description=body, colour=discord.Colour.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ServerPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)
        self.add_item(ServerPanelSelect())


async def setup(client):

    @client.tree.command(name="server", description="Open the Rovix server control panel")
    async def server(interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(
            title=f"⚡ Rovix — {guild.name}",
            description="Manage Rovix features from the menu below.",
            colour=discord.Colour.blurple()
        )
        embed.add_field(name="Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        await interaction.response.send_message(embed=embed, view=ServerPanel(), ephemeral=True)
