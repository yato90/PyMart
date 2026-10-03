import asyncio

from app.cache.redis import redis_client


async def main():
    await redis_client.set("test:key", "hello")

    value = await redis_client.get("test:key")

    print(value)

    await redis_client.delete("test:key")
    await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())