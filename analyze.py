import asyncio
from src.stats.analyze import analyze

async def main():
    analyze()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())