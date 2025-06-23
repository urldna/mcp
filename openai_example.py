from openai import OpenAI

# Initialize OpenAI client (assumes API key is set via env var or config)
client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",  # GPT-4.1 supports native tool use
    input=[
        {
            "role": "system",
            "content": [{"type": "input_text", "text": "You are a cybersecurity analyst using urlDNA."}]
        },
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "Search in urlDNA malicious scan with title like paypal"}]
        }
    ],
    text={"format": {"type": "text"}},
    reasoning={},  # Keep it empty unless you need structured explanation
    tools=[
        {
            "type": "mcp",
            "server_label": "urlDNA",
            "server_url": "https://mcp.urldna.io/sse",
            "headers": {
                "Authorization": "Bearer <URLDNA_API_KEY>"  # Replace with URLDNA API key
            },
            "allowed_tools": ["new_scan", "get_scan", "search", "fast_check"],
            "require_approval": "never"
        }
    ],
    temperature=0.7,
    top_p=1,
    max_output_tokens=2048,
    store=True
)

print(response.output)
