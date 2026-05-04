import asyncio
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from sqlalchemy import text


async def seed_admin():
    async with AsyncSessionLocal() as session:
        exists = await session.execute(
            text("SELECT id FROM usuarios WHERE email = 'admin@biagro.com.br'")
        )
        if exists.scalar_one_or_none():
            return
        await session.execute(
            text("""
                INSERT INTO usuarios (tenant_id, email, senha_hash, nome, role, ativo)
                VALUES (:tenant_id, :email, :senha_hash, :nome, :role, :ativo)
            """),
            {
                "tenant_id": 1,
                "email": "admin@biagro.com.br",
                "senha_hash": get_password_hash("admin123"),
                "nome": "Administrador",
                "role": "admin",
                "ativo": True,
            },
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_admin())
