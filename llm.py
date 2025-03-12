import sys
import requests

# Set the console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "bdc41d8567888349149e521dfb8351ce46323cbe5b28282ce32b9e13c574f8d3"  # Replace with your actual Together AI API key
MODEL = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"  # Use an available model

# Create a simple test request
payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Hello can you analyse 2 commits and tell me the difference?"}],
    "max_tokens": 7000,  # Increase token limit
    "temperature": 0.7  # Optional: Adjust creativity (0.7 is balanced)
}

# Send request to Together AI API
response = requests.post(
    "https://api.together.xyz/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json=payload
)

# Print the response
if response.status_code == 200:
    print("✅ API is working! Full Response:")
    print(response.json()["choices"][0]["message"]["content"])
else:
    print("❌ API request failed!")
    print("Status Code:", response.status_code)
    print("Response:", response.text)


# Output: