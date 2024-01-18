curl --location 'http://127.0.0.1:8000/api/prediction/LLMInsight' \
--header 'Content-Type: application/json' \
--data '{
  "useCase": "XXXXXXXXXXX_DATA_AGENT",
  "contextId": "PLANNING_AGENT",
  "preSeed_injection_map": {
    "{USER_PROMPT}": "Do you have any other prompt?"
  },
  "parameters": {
    "temperature": 0.9,
    "maxOutputTokens": 2048,
    "topP": 1
  }
}'