from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_model: str = "mistral:latest"
    vision_model: str = "llava:latest"
    ollama_url: str = "http://localhost:11434"
    
        
settings = Settings()

