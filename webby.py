from flask import Flask,Blueprint
import requests
import os
from download_bhav_copy import bhav_main
bhav_main()
bp=Blueprint("test",__name__)

j="Thomas"
# Create a directory to store downloaded files if it doesn't exist
DOWNLOAD_DIR = "/tmp"


@bp.route('/show')
def show_content():
    global j
    url = 'https://www.capitalmarket.com/research'
    file_path = os.path.join(DOWNLOAD_DIR, "research_content.html")
    app.logger.info("Here is the trick")
    print("Print Trick")
    print("This is J",j)

    try:
        # Download the webpage content
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Save the content to a file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)

        # Split content into lines and get first 50
        lines = response.text.splitlines()
        first_50_lines = lines[:50]

        # Format output with line numbers
        formatted_output = "\n".join(
            f"{i+1:2}: {line}" for i, line in enumerate(first_50_lines)
        )

        return f"<pre>Content saved to: {file_path}\n\n{formatted_output}</pre>"

    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500

@bp.route("/")
def soman():
    print("Soman Shines")
    return("Soman shines")
