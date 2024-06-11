import discord
from discord.ext import commands as cmds
from dotenv import load_dotenv
import os

load_dotenv()

OWNER = [int(i) for i in (os.getenv('OWNER')).split(',')]

# Combine roles with their emojis and colors
ROLES_DATA = {
    'ku_80': {'emoji': '🔴', 'color': discord.Color.red()},
    'ku_81': {'emoji': '🔵', 'color': discord.Color.blue()},
    'ku_82': {'emoji': '🟢', 'color': discord.Color.green()},
    'ku_83': {'emoji': '🟡', 'color': discord.Color.gold()},
    'ku_84': {'emoji': '🟣', 'color': discord.Color.purple()},
}

class RoleSelection(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmds.hybrid_command()
    async def roles(self, ctx):
        if ctx.author.id not in OWNER:
            return await ctx.reply("> You have no permission to use this command!")

        embed = discord.Embed(
            title="Role Selection",
            description="React to the emojis below to get the matching role.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="🔴: ku80, 🔵: ku81, 🟢: ku82, 🟡: ku83, 🟣: ku84")
        msg = await ctx.send(embed=embed)

        for role_name, data in ROLES_DATA.items():
            await self._ensure_role(ctx.guild, role_name, data)
            await msg.add_reaction(data['emoji'])

    async def _ensure_role(self, guild, role_name, data):
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            await guild.create_role(name=role_name, color=data['color'])
        elif role.color != data['color']:
            await role.edit(color=data['color'])

    @cmds.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self._handle_reaction(payload, add_role=True)

    @cmds.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        await self._handle_reaction(payload, add_role=False)

    async def _handle_reaction(self, payload, add_role):
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        for role_name, data in ROLES_DATA.items():
            if str(payload.emoji) == data['emoji']:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    if add_role:
                        await member.add_roles(role)
                        print(f'Added {role_name} role to {member}')
                    else:
                        await member.remove_roles(role)
                        print(f'Removed {role_name} role from {member}')
                break

async def setup(bot):
    await bot.add_cog(RoleSelection(bot))
