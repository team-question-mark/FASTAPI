from starlette.config import Config
from dotenv import load_dotenv

load_dotenv()
config = Config(".env")
DATABASE_URL = config('DATABASE_URL')
API_KEY_OPENAI = config('API_KEY_OPENAI')
API_KEY_OPENAI_JAC = config('API_KEY_OPENAI_JAC')

