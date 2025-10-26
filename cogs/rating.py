import discord
from discord.ext import commands
from discord import app_commands
import database


class Rating(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="мой_рейтинг", description="Показать ваш текущий рейтинг.")
    async def my_rating(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        score = database.get_user_rating(user_id)
        await interaction.response.send_message(f"Ваш текущий рейтинг: **{score}** ✨", ephemeral=True)

    @app_commands.command(name="топ_рейтинг", description="Показать топ-10 пользователей по рейтингу.")
    async def top_rating(self, interaction: discord.Interaction):
        top_users = database.get_top_ratings(10)

        if not top_users:
            await interaction.response.send_message("Рейтинговый список пуст.", ephemeral=True)
            return

        response_str = "🏆 **Топ-10 пользователей по рейтингу:** 🏆\n\n"
        for i, (user_id, score) in enumerate(top_users):
            member = interaction.guild.get_member(user_id)
            user_name = member.display_name if member else f"Пользователь ID: {user_id}"
            response_str += f"{i + 1}. **{user_name}**: {score} очков\n"

        await interaction.response.send_message(response_str, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Rating(bot))