# Core trading loop
# This file will contain the main trading bot logic 
import logging
import openai
import os
from dotenv import load_dotenv

#Setup
load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')