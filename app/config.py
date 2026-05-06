from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "HYDRA"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./hydra.db"
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "hello@drinkhydra.com"
    BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()
