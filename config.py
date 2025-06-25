import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    chroma_persist_directory: str = "./chroma_db"
    max_chunk_size: int = 500
    chunk_overlap: int = 50
    max_scrape_pages: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()