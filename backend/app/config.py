from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The frontend is built into a "static" folder next to this package at image build time.
_PACKAGE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Mounted data volume: the SQLite file and photos live here, so a backup is one folder copy.
    data_dir: Path = Path("data")
    # Built frontend (index.html + assets). Absent during local dev — then the API runs alone.
    static_dir: Path = _PACKAGE_DIR / "static"

    @property
    def photos_dir(self) -> Path:
        return self.data_dir / "photos"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'dahlia.db'}"


settings = Settings()
