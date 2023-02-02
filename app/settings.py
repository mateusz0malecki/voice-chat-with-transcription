from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_db: str
    postgres_password: str
    postgres_host: str
    postgres_port: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_tls: bool
    mail_ssl: bool
    use_credentials: bool
    validate_certs: bool

    root_path: str
    domain: str
    recordings_path: str
    transcriptions_path: str

    storage_credentials_file: str
    bucket_name: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings():
    return Settings()
