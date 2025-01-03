import os
from dotenv import load_dotenv
from pathlib import Path

# Require Root Dir
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file
load_dotenv(dotenv_path=BASE_DIR / '.env')

# .env file loaded, use os.getenv() to retrieve variables
USER_NAME = os.getenv('USER_NAME')
USER_PASSWORD = os.getenv('USER_PASSWORD')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_ENDPOINT = os.getenv('LANGCHAIN_ENDPOINT')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
LOCAL_FOLDER = fr"{os.getenv('LOCAL_FOLDER')}"
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# can use os.environ if need environment variables
os.environ['LANGCHAIN_TRACING_V2'] = LANGCHAIN_TRACING_V2
os.environ['LANGCHAIN_ENDPOINT'] = LANGCHAIN_ENDPOINT
os.environ['LANGCHAIN_API_KEY'] = LANGCHAIN_API_KEY
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Other environ
# ...
