import pathlib

from starlette.config import Config

base_path = pathlib.Path(__file__).parent.absolute()
config_path = base_path / ".env"
config = Config(env_file=config_path)

DB_CONN_STRING: str = config.get(
    "DB_CONN_STRING",
    cast=str,
    default="sqlite+aiosqlite:///:memory:",
)
DB_ECHO: bool = config.get("DB_ECHO", cast=bool, default=False)
DB_POOL_SIZE: int = config.get("DB_POOL_SIZE", cast=int, default=10)
DB_MAX_OVERFLOW: int = config.get("DB_MAX_OVERFLOW", cast=int, default=10)

JWT_SECRET_KEY: str = config.get(
    "JWT_SECRET_KEY",
    cast=str,
    default="bac8af31f79b167f7f698ac1962449d09106e6fcefa1394baa4e294c9b8a55bc",
)
