import re


# Function to parse a promt to an array countaining the service, the type and the value of the request
def parse(input: str):
    match = re.match(r"(http[s]?://)?([a-zA-Z.]+)(/(.*)?)?", input)
    # Check if the input is a link
    if match:
        URLparts = match.group(2).split(".")
        # Obtain the URL parts
        domain = ".".join(URLparts[-2:])
        path = match.group(4)
        # If the path is empty
        if path is None:
            return {"type": "error", "value": "A complete link must be given"}
        # Check if the service is youtube
        if domain in ["youtube.com", "youtu.be"]:
            return youtubeParse(path)
        # If the service is not supported
        return {"type": "error", "value": "Not supported link"}
    # If the promt is a search query
    return {"service": "youtube", "type": "search_query", "value": input}


# Subfunction of parse, works only for youtube with the path of the link
def youtubeParse(path):
    match = re.match(r"((results|watch|playlist)\?)?(.*)", path)
    # Check if the path is valid
    if match:
        # Check if the path includes arguments
        if match.group(1) is None:
            # Check if all the chars in the path are valid for the video id
            if re.match(r"^[a-zA-Z0-9]+$", path):
                return {"service": "youtube", "type": "v", "value": path}
        else:
            # Get the link args
            args = match.group(3).split("&")
            for arg in args:
                key, value = arg.split("=", 1)
                # Check for valid arguments
                if key in ["search_query", "v", "list"]:
                    return {"service": "youtube", "type": key, "value": value}
    # If no return yet, return an error
    return {"service": "youtube", "type": "error", "value": "Invalid URL"}
