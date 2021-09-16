from flask import request

def transform_book_res(data):
    """Takes the response from Open Library's Works API and transforms into an instance of the Book model"""

    try:
        title = data["title"]
    except:
        title = "Title not available"
    try:
        author = data["authors"][0]["name"]
    except:
        author = "Author not available"
    try:
        image = data["cover"]['medium']
    except:
        image = "/static/images/placeholder.png"
    try:
        num_pages = data["number_of_pages"] or None,
    except:
        num_pages = "Number of pages not available"
    try:
        publish_date = data["publish_date"]
    except:
        publish_date = "Publish date not available"

    return {
        "title": title, 
        "author": author, 
        "image": image,
        "num_pages": num_pages,
        "publish_date": publish_date
    }