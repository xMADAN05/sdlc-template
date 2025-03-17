from langchain_openai import ChatOpenAI

from core.config import config

# Initialize LLM
llm = ChatOpenAI(
    model=config.LLM_MODEL,
    temperature=config.LLM_TEMPERATURE,
)