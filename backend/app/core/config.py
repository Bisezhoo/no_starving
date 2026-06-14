from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    openrouter_api_key: str = Field(alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(alias="OPENROUTER_MODEL")
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    mealdb_base_url: str = Field("https://www.themealdb.com/api/json/v1/1", alias="MEALDB_BASE_URL")
    cocktaildb_base_url: str = Field("https://www.thecocktaildb.com/api/json/v1/1", alias="COCKTAILDB_BASE_URL")
    agent_max_tool_calls: int = Field(6, alias="AGENT_MAX_TOOL_CALLS")
    agent_max_llm_steps: int = Field(4, alias="AGENT_MAX_LLM_STEPS")
    log_full_system_prompt: bool = Field(False, alias="LOG_FULL_SYSTEM_PROMPT")
    log_full_user_message: bool = Field(False, alias="LOG_FULL_USER_MESSAGE")
    log_full_source_text: bool = Field(False, alias="LOG_FULL_SOURCE_TEXT")
    log_sensitive_external_headers: bool = Field(False, alias="LOG_SENSITIVE_EXTERNAL_HEADERS")
    log_stack_trace: bool = Field(False, alias="LOG_STACK_TRACE")

    @field_validator("openrouter_api_key", "openrouter_model")
    @classmethod
    def require_non_blank(cls, value: str, info):
        if not value or not value.strip():
            raise ValueError(f"{info.field_name.upper()} is required")
        return value.strip()
