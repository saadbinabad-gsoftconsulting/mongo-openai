from mongo_agent4 import process_query

query = "Find the total number of records in the dataset."  
result = process_query(query)

if result["error"]:
    print(f"Error: {result['error']}")
else:
    print("Generated Pipeline:")
    print(result["pipeline"])
    print("Query Results:")
    print(result["results"])
