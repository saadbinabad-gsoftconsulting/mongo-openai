import os
import pymongo
import openai
from dotenv import load_dotenv, find_dotenv
import json  # For safer handling of API responses

# Load environment variables from .env file
load_dotenv(find_dotenv())

# OpenAI Setup
openai.api_key = os.getenv('OPENAI_API_KEY')

# MongoDB Setup
mongo_client = pymongo.MongoClient("mongodb+srv://saad:gsoft2hai@cluster0.ekcwi.mongodb.net/")
db = mongo_client["Solar"]
collection = db["SolarInfo"]

# Functions for prompt creation
def get_system_prompt():
    return ("You are an assistant that generates MongoDB aggregation pipelines based on user input. "
           "The MongoDB collection has the following fields: Location (string), No_of_Bedrooms (integer), "
           "No_of_Heavy_Appliances (integer), Monthly_Electricity_Bill (integer), Suitable_Solar_System (string). "
           "Use these exact field names and generate only the pipeline as a valid JSON list without explanations.")

def get_user_prompt(natural_language_query):
    return f"Generate a MongoDB aggregation pipeline to satisfy the following query:\n\n'{natural_language_query}'\n\nProvide the pipeline as a valid JSON list."

def generate_mongodb_pipeline(natural_language_query, model="gpt-4"):
    system_prompt = get_system_prompt()
    user_prompt = get_user_prompt(natural_language_query)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Generate completion using OpenAI API
    chat_completion = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    assistant_response = chat_completion.choices[0].message.content.strip()
    print(f"Assistant Response:\n{assistant_response}")

    # Parse the assistant's response as JSON
    try:
        pipeline = json.loads(assistant_response)
        return pipeline

    except json.JSONDecodeError:
        return "Error: Unable to parse the assistant's response as a valid JSON pipeline."

# Example usage
natural_language_query = "Find all solar systems suitable for houses with more than 4 bedrooms in California, sorted by electricity bill in descending order."
pipeline = generate_mongodb_pipeline(natural_language_query)

if isinstance(pipeline, list):  # Check if the response is a valid pipeline
    print("Generated MongoDB Aggregation Pipeline:")
    print(json.dumps(pipeline, indent=4))
else:
    print(pipeline)
    
    
try:
    # Execute the query and retrieve the results
    results = collection.aggregate(pipeline)
    
    # Format and print the results
    response = "Based on your query, here are the results:\n\n"
    for i, doc in enumerate(results, start=1):
        response += (f"{i}. Bedrooms: {doc['No_of_Bedrooms']}, Appliances: {doc['No_of_Heavy_Appliances']}, "
                     f"Electricity Bill: ${doc['Monthly_Electricity_Bill']}, Location: {doc['Location']}, "
                     f"Recommended Solar System: {doc['Suitable_Solar_System']}\n\n")
    print(response)
except Exception as e:
    print(f"Error: {e}")