import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_random_exponential


class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    async def summarize_text(
        self, text: str, model: str = "gemini-1.5-flash", length_instruction: str = ""
    ) -> str:
        try:
            # For Gemini, we can directly use the generate_content method
            # The prompt can be a single string or a list of parts
            prompt = (
                f"Please summarize the following text: {length_instruction}\n\n{text}"
            )

            # Use the GenerativeModel for chat-like interactions
            model_instance = genai.GenerativeModel(model)
            response = await model_instance.generate_content_async(prompt)

            return response.text.strip()
        except Exception as e:
            # Log the exception for debugging
            print(f"Error during summarization: {e}")
            raise
