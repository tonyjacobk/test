from flask import Flask
import requests
import os

app = Flask(__name__)

# Create a directory to store downloaded files if it doesn't exist
DOWNLOAD_DIR = "/tmp"


@app.route('/show')
def show_content():
    url = 'https://www.capitalmarket.com/research'
    file_path = os.path.join(DOWNLOAD_DIR, "research_content.html")

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

if __name__ == '__main__':
 app.run(host='0.0.0.0',debug=True)

