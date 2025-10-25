from discord.ext import commands

class Rating(commands.Cog):
    """Система рейтингов пользователей."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="рейтинг")
    async def show_rating(self, ctx):
        """Показать рейтинг пользователей (заглушка)."""
        await ctx.send("Рейтинги пока не реализованы.")

async def setup(bot):
    await bot.add_cog(Rating(bot))
