import os
from dotenv import load_dotenv

load_dotenv()

# MYSQL
MYSQL_HOST = os.getenv('MYSQL_HOST')
try:
    MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
except TypeError:
    print("MYSQL_PORT is not set, use default port 3306")
    MYSQL_PORT = 3306
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
# CROWDIN
TOKEN = os.getenv('TOKEN')
PROJECT_ID = os.getenv('PROJECT_ID')
BRANCH_NAME = os.getenv('BRANCH_NAME')
PROJECT_START_YEAR = int(os.getenv('PROJECT_START_YEAR'))
PROJECT_START_MONTH = int(os.getenv('PROJECT_START_MONTH'))
PROJECT_START_DAY = int(os.getenv('PROJECT_START_DAY'))
IGNORED_MEMBERS = os.getenv('IGNORED_MEMBERS').split(',')
# REWARD SYSTEM
REWARD_MESSAGE = os.getenv('REWARD_MESSAGE')
CODE_SYSTEM_KEY = os.getenv('CODE_SYSTEM_KEY')