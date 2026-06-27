import httpx
from typing import Dict, Any

class AIProviderFactory:
    @staticmethod
    async def call_llm(provider: str, model_name: str, temperature: float, system_prompt: str, user_input: str, api_key: str) -> str:
        headers = {}
        payload = {}
        
        if provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            }
            
        elif provider == "anthropic":
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            payload = {
                "model": model_name,
                "max_tokens": 4000,
                "temperature": temperature,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_input}]
            }
            
        elif provider == "gemini":
            # Native Google Cloud API execution paths
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{"text": f"{system_prompt}\n\nUser Input: {user_input}"}]
                }],
                "generationConfig": {"temperature": temperature}
            }
        else:
            raise ValueError(f"Provider {provider} not supported.")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                raise Exception(f"AI Provider Error ({response.status_code}): {response.text}")
            
            resp_json = response.json()
            if provider == "openai":
                return resp_json["choices"][0]["message"]["content"]
            elif provider == "anthropic":
                return resp_json["content"][0]["text"]
            elif provider == "gemini":
                return resp_json["candidates"][0]["content"]["parts"][0]["text"]
