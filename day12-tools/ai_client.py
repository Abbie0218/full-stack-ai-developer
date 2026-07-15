from groq import Groq
import os
from dotenv import load_dotenv
from tenacity import retry, retry_if_exception_type,wait_exponential,stop_after_attempt
from groq._exceptions import RateLimitError
load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL')

def extract_text(response)->str:
    try:
        return response.choices[0].message.content
    except Exception:
        return ""

# Retry with exponential backoff


@retry(
    retry=retry_if_exception_type(RateLimitError), 
    wait=wait_exponential(multiplier=1,min=1,max=5),
    stop=stop_after_attempt(5)
)
def ask_with_retry(question:str, model:str=DEFAULT_MODEL):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":question}],
        max_tokens=200
    )
    return extract_text(response)
