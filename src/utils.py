import random


def get_header():
    """Gets a random user agent and returns it as a header.

    :return: A dictionary containing the header with a User-Agent
    :rtype: dict
    """
    agent_list = []

    # List of browsers (each browser has a text file with UA)
    browser_list = [
        "Firefox",
        "Internet+Explorer",
        "Opera",
        "Safari",
        "Chrome",
        "Edge",
        "Android+Webkit+Browser",
    ]

    # Randomly select which file browser to read
    browser = random.choice(browser_list)

    # File path
    file_path = f"../data/user_agents/{browser}.txt"

    with open(file_path, "r") as file:
        for line in file:
            if not line.startswith("More"):
                # Remove newline character and leading/trailing whitespace
                cleaned_line = line.strip()
                agent_list.append(cleaned_line)
    user_agent = random.choice(agent_list)
    header = {"User-Agent": user_agent}
    return header


def write_file(text, filename):
    """Writes to a text file
    :param text: text to be written to the file
    :param filename: name of the file"""
    with open(filename, "w") as f:
        f.write(text)


def read_file(filename):
    """Reads from a file
    :param filename: name of the file to be read
    :return: contents of the file
    :rtype: string"""
    with open(filename, "r") as f:
        file_content = f.read()
    return file_content
