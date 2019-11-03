from bot import Hmmm
from dotenv import load_dotenv
from os import getenv


def main():
    load_dotenv()
    hmm = Hmmm()
    hmm.run(getenv("DISCORD_TOKEN"))
