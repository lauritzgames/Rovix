import discord
from discord import app_commands


async def setup(client):

    @client.tree.command(
        name="deletecategory",
        description="Delete a category and all channels inside it"
    )
    @app_commands.describe(
        category="The category to delete"
    )
    async def deletecategory(
        interaction: discord.Interaction,
        category: discord.CategoryChannel
    ):
        await interaction.response.defer(ephemeral=True)

        channels = list(category.channels)

        deleted_channels = 0

        for channel in channels:
            try:
                await channel.delete(
                    reason=f"Category deletion requested by {interaction.user}"
                )
                deleted_channels += 1

            except discord.HTTPException:
                continue

        try:
            await category.delete(
                reason=f"Category deletion requested by {interaction.user}"
            )

        except discord.HTTPException:
            await interaction.followup.send(
                "❌ I couldn't delete the category.",
                ephemeral=True
            )
            return

        await interaction.followup.send(
            f"✅ Deleted `{category.name}` and `{deleted_channels}` channel(s) inside it.",
            ephemeral=True
        )