from pydantic import BaseModel


class LLMConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int | None = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    top_k: int | None = None        # llama.cpp / Ollama specific
    min_p: float | None = None      # llama.cpp / Ollama specific


class PromptConfig(BaseModel):
    style_notes: str = ""


class CategoryTemplate(BaseModel):
    name: str
    description: str = ""
    llm: LLMConfig = LLMConfig()
    prompts: PromptConfig = PromptConfig()


class ResolvedConfig(BaseModel):
    llm: LLMConfig
    prompts: PromptConfig
    template: CategoryTemplate
