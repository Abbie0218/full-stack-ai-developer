import requests


# tool definitions

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "We can use this function to get latest temperature and other details for given city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Enter the city name for which we need to know weather details",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Will return the result of any expression passed into that",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Use this to perform eval and return result",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Will search for the query in the existing notes and return note object",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {  # ✅ object not string
                        "type": "string",
                        "description": "keyword",
                    }
                },
                "required": ["query"],
            },
        },
    },
]


def calculate(expression: str):
    result = eval(expression)
    return result


def get_weather(city: str):
    api_key = "0e59b200d43dee08dd8e7a03d7717ea5"

    if not city.strip():
        return print("please pass city")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)
    data = response.json()

    temperature = data["main"]["temp"]
    details = data["weather"][0]["description"]

    return {"city": city, "temperature": temperature, "condition": details}




def search_notes(query: str):
    fake_notes = [
        {"id": 1, "title": "Meeting notes", "tag": "work"},
        {"id": 2, "title": "Study plan", "tag": "study"},
        {"id": 3, "title": "Shopping list", "tag": "personal"},
    ]

    if not query.strip():
        return print("please pass query")
    results = []
    for note in fake_notes:
        if query.lower() in note["title"].lower():
            results.append(note)
    if not results:
        print(f"No result found")

    return results



