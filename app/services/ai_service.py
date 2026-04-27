import os
from dotenv import load_dotenv
from groq import AsyncGroq 
import json

load_dotenv()

# 1. Initialize Client ONCE globally (Efficient)
client = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))

async def generate_slugs(description: str):
   """
   Takes a website description and returns 3 short slugs.
   """
   try:
      chat_completion = await client.chat.completions.create(
         messages=[
            {
               'role': 'system',
               'content':'You are a specialized URL short slug generator. Return a JSON object with a key "slugs" containing 1 short, hyphenated options.'
            },
            {
               'role':'user',
               'content': description
            }
         ],
         model='llama-3.3-70b-versatile',
         response_format={"type": "json_object"} # Force JSON so your code can read it
      )
      """ Parse the response into a string before passing over to /endpoints """
      # parse json to python dictionary
      data_dict = json.loads(chat_completion.choices[0].message.content)
      # get the key slugs
      data_key = data_dict.get('slugs')
      # parse list value to string
      slug = ''.join(data_key)
      return slug

   except Exception as e:
      print(f"Error generating slugs: {e}")
      return None
