from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    project_name: str = "Group watching service"

    postgres_db: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5431
    echo_in_db: bool = False

    log_file: str


settings = Settings()
