from google import genai

# The new SDK uses a unified Client object
client = genai.Client(api_key="")

# Generate content using the new stateless method
response = client.models.generate_content(
    model="model = genai.GenerativeModel('models/gemini-1.5-flash')", 
    contents="Explain why I had to update my library."
)

print(response.text)
