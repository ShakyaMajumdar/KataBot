from typing import Dict

from discord.ext import commands
import discord


import aiohttp
from bs4 import BeautifulSoup

import sqlite3

import random


class Challenge(commands.Cog):
    """
    Get random programming challenges(katas), uses the Codewars API
    """

    def __init__(self, bot):
        self.bot = bot
        self.CODEWARS_SEARCH_URL = "https://www.codewars.com/kata/search/?q=&&beta=false"
        self.CODEWARS_GET_KATA_ENDPOINT = "https://www.codewars.com/api/v1/code-challenges/"

    @commands.command()
    async def update_kata_db(self, ctx: commands.Context) -> None:
        """
        Search Codewars for newest katas and update katas.db.
        Database is created automatically if it is not found
        :param ctx: context of command invocation
        :return: None
        """

        db_connection = sqlite3.connect('katas.db')
        db_cursor = db_connection.cursor()

        db_cursor.execute('''
        CREATE TABLE IF NOT EXISTS katas
        (id, name, description, created by, creator url, kata url, difficulty, 
        UNIQUE(id))''')

        async with aiohttp.ClientSession() as session:
            async with session.get(self.CODEWARS_SEARCH_URL) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                kata_divs = soup.find_all("div", class_="kata")

                for div in kata_divs:
                    kata_id = div['id']
                    async with session.get(f"{self.CODEWARS_GET_KATA_ENDPOINT}{kata_id}") as api_response:
                        resp = await api_response.json()
                        if len(resp['description']) > 1024:
                            continue
                        db_cursor.execute(
                            '''INSERT INTO katas VALUES (?, ?, ?, ?, ?, ?, ?)''', (
                                resp['id'],
                                resp['name'],
                                resp['description'],
                                resp['createdBy']['username'],
                                resp['createdBy']['url'],
                                resp['url'],
                                resp['rank']['name']
                            )
                        )

        db_connection.commit()
        db_connection.close()

        await ctx.send("Updated!")

    @staticmethod
    def get_random_kata() -> Dict:
        """
        Fetches a random kata from the database
        :return: dict of information of a random kata
        """
        db_connection = sqlite3.connect('katas.db')
        db_cursor = db_connection.cursor()
        kata = db_cursor.execute('''
        SELECT * FROM katas 
        ORDER BY RANDOM() LIMIT 1
        ''').fetchone()
        return dict(zip(("id", "name", "description", "created by", "creator url", "kata url", "difficulty"), kata))

    @commands.command()
    async def send_kata(self, ctx: commands.Context) -> None:
        """
        Formats and sends a random kata
        """

        kata = self.get_random_kata()

        embed = discord.Embed(
            title=f"{kata['name']}",
            url=kata['kata url'],
            color=random.randint(0, 0xffffff)
        )

        embed.add_field(name="Difficulty", value=kata["difficulty"], inline=False)
        embed.add_field(name=f"Problem Statement", value=kata["description"])

        embed.add_field(
            name="Created by",
            value=f"[{kata['created by']}]({kata['creator url']})",
            inline=False
        )

        embed.add_field(name="ID", value=kata["id"])

        await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    """Kata Challenges Cog load."""
    print("adding kata cog")
    bot.add_cog(Challenge(bot))
