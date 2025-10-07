import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "false").lower() == "true"

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "0") or 0)
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"


def get_config():
    # Priority: ENV then FLASK_ENV
    env = os.getenv("ENV") or os.getenv("FLASK_ENV") or "production"
    env = env.lower()
    if env.startswith("dev"):
        return DevelopmentConfig
    return ProductionConfig
