import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential


class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = self.api_key

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    async def summarize_text(
        self, text: str, model: str = "gpt-3.5-turbo", length_instruction: str = ""
    ) -> str:
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes academic papers.",
                },
                {
                    "role": "user",
                    "content": f"Please summarize the following text: {length_instruction}\n\n{text}",
                },
            ]
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Log the exception for debugging
            print(f"Error during summarization: {e}")
            raise
