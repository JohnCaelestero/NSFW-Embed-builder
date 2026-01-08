#!/usr/bin/env python3
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import logging
import os
import io
import re
from bs4 import BeautifulSoup

# ---------- CONFIG ----------
ARCHIVE_CHANNEL_ID = ID
USER_AGENT = "Mozilla/5.0 (EmbedBot/3.1)"

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("EmbedBot")

# ---------- Load secrets ----------
with open(os.path.join(BASE_DIR, "token.txt")) as f:
    TOKEN = f.read().strip()

with open(os.path.join(BASE_DIR, "serverID.txt")) as f:
    GUILD_ID = int(f.read().strip())

# ---------- Bot ----------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

session: aiohttp.ClientSession | None = None

# ---------- Regex ----------
PH_REGEX = r"https?://(?:www\.)?pornhub\.com/view_video\.php\?viewkey=[\w-]+"
XV_REGEX = r"https?://(?:www\.)?xvideos\.com/video\.\w+/\w+"
TENOR_REGEX = r"https?://(?:www\.)?tenor\.com/view/\S+"

# ---------- Media colors ----------
MEDIA_COLORS = {
    "PH": discord.Color.orange(),
    "XV": discord.Color.red(),
    "GIF": discord.Color.purple(),
    "IMAGE": discord.Color.blue(),
    "VIDEO": discord.Color.green(),
}

# ---------- Helpers ----------
def attachment_type(att: discord.Attachment) -> str | None:
    name = att.filename.lower()
    if name.endswith(".gif"):
        return "GIF"
    if name.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return "IMAGE"
    if name.endswith((".mp4", ".webm", ".mov")):
        return "VIDEO"
    return None

async def fetch_metadata(url: str):
    try:
        async with session.get(url, headers={"User-Agent": USER_AGENT}) as res:
            html = await res.text()

        soup = BeautifulSoup(html, "html.parser")
        title = soup.find("meta", property="og:title")
        image = soup.find("meta", property="og:image")

        return (
            title["content"] if title else "Media",
            image["content"] if image else None
        )
    except Exception:
        logger.exception("Metadata fetch failed")
        return "Media", None

async def archive_thumbnail(title: str, image_url: str | None):
    if not image_url:
        return None

    try:
        async with session.get(image_url) as res:
            data = await res.read()

        channel = bot.get_channel(ARCHIVE_CHANNEL_ID)
        if not channel:
            return None

        file = discord.File(io.BytesIO(data), filename="thumb.jpg")
        msg = await channel.send(content=title, file=file)
        return msg.attachments[0].url
    except Exception:
        logger.exception("Thumbnail archive failed")
        return None

def build_embed(*, title=None, url=None, image=None, color, author):
    embed = discord.Embed(title=title, url=url, color=color)
    if image:
        embed.set_image(url=image)
    embed.set_author(
        name=author.display_name,
        icon_url=author.display_avatar.url
    )
    return embed

# ---------- Core processor ----------
async def process_message(message: discord.Message) -> bool:
    if message.author.bot:
        return False

    # Skip messages already processed / embedded
    if message.embeds:
        return False

    embedded = False

    # Shared title for all attachments in this message
    title_text = message.content.strip() or None

    # ---------- Attachments ----------
    for att in message.attachments:
        media = attachment_type(att)
        if not media:
            continue

        file = await att.to_file()

        if media == "VIDEO":
            # Video: embed title on top, playable video below
            embed = build_embed(
                title=title_text or att.filename,
                color=MEDIA_COLORS["VIDEO"],
                author=message.author
            )
            await message.channel.send(embed=embed, file=file)

        else:
            # Image / GIF: NO filename fallback
            embed = build_embed(
                title=title_text,
                image=f"attachment://{file.filename}",
                color=MEDIA_COLORS[media],
                author=message.author
            )
            await message.channel.send(embed=embed, file=file)

        embedded = True

    # ---------- Links ----------
    links = (
        re.findall(PH_REGEX, message.content)
        + re.findall(XV_REGEX, message.content)
        + re.findall(TENOR_REGEX, message.content)
    )

    for link in links:
        if "pornhub" in link:
            source = "PH"
        elif "xvideos" in link:
            source = "XV"
        else:
            source = "GIF"

        title, image = await fetch_metadata(link)
        image = await archive_thumbnail(title, image) or image

        embed = build_embed(
            title=title,
            url=link,
            image=image,
            color=MEDIA_COLORS[source],
            author=message.author
        )
        await message.channel.send(embed=embed)
        embedded = True

    # ---------- Cleanup ----------
    if embedded:
        try:
            await message.delete()
        except discord.Forbidden:
            pass

    return embedded

# ---------- Slash command ----------
@app_commands.command(
    name="refresh_server",
    description="Scan entire server and embed un-embedded media"
)
async def refresh_server(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    count = 0
    for channel in interaction.guild.text_channels:
        try:
            async for msg in channel.history(limit=None, oldest_first=True):
                if await process_message(msg):
                    count += 1
                    await asyncio.sleep(0.25)
        except discord.Forbidden:
            continue

    await interaction.followup.send(
        f"✅ Refresh complete. {count} messages embedded.",
        ephemeral=True
    )

# ---------- Events ----------
@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    logger.info("✅ Logged in as %s", bot.user)

@bot.event
async def on_message(message: discord.Message):
    await process_message(message)
    await bot.process_commands(message)

# ---------- Register ----------
bot.tree.add_command(refresh_server, guild=discord.Object(id=GUILD_ID))

# ---------- Run ----------
bot.run(TOKEN)
