# app/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    # JWT settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


# Create a single, reusable instance of the settings
settings = Settings()
