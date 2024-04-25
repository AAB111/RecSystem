from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_PASS: str
    DB_USER: str
    API_KEY: str
    DB_SCHEMA: str
    SECRET: str
    @property
    def database_url(self):
        DATABESE_URL = F'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        return DATABESE_URL

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
