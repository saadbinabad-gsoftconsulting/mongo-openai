import os
import pymongo
import openai
from dotenv import load_dotenv, find_dotenv
import json  # For safer handling of API responses


def process_query(natural_language_query, model="gpt-4"):
    
    # Load environment variables from .env file
    load_dotenv(find_dotenv())

    # OpenAI Setup
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # MongoDB Setup
    mongo_client = pymongo.MongoClient(
        "mongodb+srv://saad:gsoft2hai@cluster0.ekcwi.mongodb.net/"
    )
    db = mongo_client["Solar"]
    collection = db["SolarInfo"]

    # Fetch one document from the collection to get the schema
    sample_document = collection.find_one()

    # Convert the document to a dictionary and get the keys
    if sample_document:
        fields = list(sample_document.keys())
    else:
        fields = []

    # Functions for prompt creation
    def get_system_prompt():
        fields_str = ", ".join(
            [f"{field} (type: {type(value).__name__})" for field, value in sample_document.items()]
        )
        return (
            f"You are an assistant that generates MongoDB aggregation pipelines based on user input. "
            f"The MongoDB collection has the following fields: {fields_str}. "
            "Use these exact field names and generate only the pipeline as a valid JSON list without explanations."
        )

    def get_user_prompt(natural_language_query):
        return f"Generate a MongoDB aggregation pipeline to satisfy the following query:\n\n'{natural_language_query}'\n\nProvide the pipeline as a valid JSON list."

    def generate_mongodb_pipeline():
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
            temperature=0,
        )

        assistant_response = chat_completion.choices[0].message.content.strip()
        print(f"Assistant Response:\n{assistant_response}")

        # Parse the assistant's response as JSON
        try:
            pipeline = json.loads(assistant_response)
            return pipeline
        except json.JSONDecodeError:
            return {"error": "Unable to parse the assistant's response as a valid JSON pipeline."}

    # Generate the pipeline
    pipeline = generate_mongodb_pipeline()

    if isinstance(pipeline, dict) and "error" in pipeline:
        return {"pipeline": None, "results": None, "error": pipeline["error"]}

    # Execute the query
    try:
        results = list(collection.aggregate(pipeline))
        return {"pipeline": pipeline, "results": results, "error": None}
    except Exception as e:
        return {"pipeline": pipeline, "results": None, "error": str(e)}
