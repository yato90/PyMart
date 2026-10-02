import asyncio
from getpass import getpass

from sqlalchemy import select

from app.auth.password import hash_password
from app.database.connection import AsyncSessionLocal
from app.database.models.user import User


async def create_admin() -> None:
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password: ")

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            print("User with this email already exists.")
            return

        user = User(
            email=email,
            password_hash=hash_password(password),
            is_admin=True,
        )

        session.add(user)
        await session.commit()

        print(f"Admin created: {email}")


if __name__ == "__main__":
    asyncio.run(create_admin())