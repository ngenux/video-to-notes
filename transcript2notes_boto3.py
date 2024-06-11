import boto3
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
# Variables for bedrock API
modelId = "anthropic.claude-3-sonnet-20240229-v1:0"  # change this to use a different version from the model provider
accept = "application/json"
contentType = "application/json"

prompt_subject = "prompt_template1"  # example prompt

# Load the text data
logging.info("Loading text data...")
with open("sample.json", 'r') as file:
    data = json.load(file)

# Load the prompts
logging.info("Loading prompts...")
with open("prompts.json", 'r') as file:
    prompts = json.load(file)

template = prompts[prompt_subject]
prompt = prompts['prompt_template1'].format(text=data['text'])

# Messages
messages = [{
    "role": "user",
    "content": [
        {
            "type": "text",
            "text": f"{prompt}"
        }
    ]
}]
# Body
body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": messages
})

# Run bedrock API
logging.info("Invoking Bedrock API...")
response = bedrock_runtime.invoke_model(
    modelId=modelId,
    contentType=contentType,
    accept=accept,
    body=body
)

# Print response
logging.info("Processing response...")
response_body = json.loads(response.get('body').read())
response_text = response_body['content'][0]['text']

logging.info("Response received. Printing notes...")
print(response_text)