import requests

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Assuming the response is in JSON format
    else:
        response.raise_for_status()

def format_data(data):
    # Example formatting function
    formatted_data = {
        "title": data.get("title"),
        "author": data.get("author"),
        "isbn": data.get("isbn"),
        "publisher": data.get("publisher"),
        "published_date": data.get("published_date"),
    }
    return formatted_data

if __name__ == "__main__":
    isbn = "978-1098106744"
    url = f"https://annas-archive.org/search?q={isbn}"
    data = fetch_data(url)
    formatted_data = format_data(data)
    print(formatted_data)