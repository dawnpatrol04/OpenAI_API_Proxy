from langchain.llms import BaseLLM
from pydantic import BaseModel, Field
import requests

class MyCustomLLMConfig(BaseModel):
    api_url: str = Field(...)

class MyCustomLLM(BaseLLM):
    def __init__(self, config: MyCustomLLMConfig):
        super().__init__(config)
        self.api_url = config.api_url

    def _generate(self, prompt, **kwargs):
        # Your existing _generate implementation

        def _llm_type(self):
            return "CustomAPI"

# Usage
config = MyCustomLLMConfig(api_url="http://localhost:8080/api/prediction/LLMInsight")
my_llm = MyCustomLLM(config)

# Use the LLM
response = my_llm.generate("Your prompt here")
print(response)
