import requests

# FastAPI endpoint
url = "http://localhost:8000/copilot/rag-process"

# Prompt to test
prompt = "can you give me a financial report for this file here and how i can make money from such an opportunity?"

# Full file path to your local PDF
file_path = r""

# Send POST request with file and prompt
with open(file_path, "rb") as f:
    files = {"file": ("my_test_file.pdf", f, "application/pdf")}
    data = {"prompt": prompt}

    response = requests.post(url, data=data, files=files)

# Print result
print("Status Code:", response.status_code)
try:
    print("Response JSON:")
    print(response.json())
except Exception:
    print("Raw Response:")
    print(response.text)
