from sqlalchemydemo.base import Base
from sqlalchemydemo.db import engine
import pkgutil
from pathlib import Path
import asyncio

# 创建数据库
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":

    package_dir = Path("./sqlalchemydemo/models").resolve()
    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix="sqlalchemydemo.models.",
    )
    for module in modules:
        __import__(module.name) 

    asyncio.run(create_db())


