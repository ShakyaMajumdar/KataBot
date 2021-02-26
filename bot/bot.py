import os

from aiohttp import ClientSession
from discord.ext import commands

from . import constants


class Bot(commands.Bot):
    """The core of the bot."""

    def __init__(self) -> None:

        self.http_session = ClientSession()
        super().__init__(command_prefix=constants.PREFIX)
        self.load_extensions()

    def load_extensions(self) -> None:
        """Load all the extensions in the exts/ folder."""

        for extension in constants.EXTENSIONS.glob("*.py"):
            if extension.name.startswith("_"):
                continue  # ignore files starting with _
            dot_path = str(extension).replace(os.sep, ".")[:-3]  # remove the .py

            self.load_extension(dot_path)

    def run(self) -> None:
        """Run the bot with the token in constants.py/.env ."""
        if constants.TOKEN is None:
            raise EnvironmentError(
                "token value is None. Make sure you have configured the TOKEN field in .env"
            )
        super().run(constants.TOKEN)

    async def on_ready(self) -> None:
        """Run when the bot has connected to discord and is ready."""
        print('Bot online!')

    async def close(self) -> None:
        """Close Http session when bot is shutting down."""
        print("shutdown")
        await super().close()

        if self.http_session:
            await self.http_session.close()
