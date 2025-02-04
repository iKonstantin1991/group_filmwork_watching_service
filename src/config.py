from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    project_name: str = "Group watching service"

    postgres_db: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    echo_in_db: bool = False

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379

    service_login: str
    service_password: str

    auth_service_host: str = "127.0.0.1"
    auth_service_port: int = 80
    jwt_public_key: bytes

    content_service_url: str = "http://localhost:81"
    notification_service_url: str = "http://localhost:82"

    template_id_completed_reservation: UUID
    template_id_cancelled_reservation: UUID

    log_file: str

    debug: bool = True


settings = Settings()  # type: ignore[call-arg]
