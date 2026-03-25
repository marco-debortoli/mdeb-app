from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    allowed_origins: str = "http://localhost:5173"
    garmin_email: str = ""
    garmin_password: str = ""
    garmin_tokenstore: str = "/tmp/garth_tokens"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


settings = Settings()
