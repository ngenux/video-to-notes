import boto3
import json
import os
import sys
import logging

from langchain import PromptTemplate
from langchain.docstore.document import Document
from langchain_aws import BedrockLLM, ChatBedrock
from langchain.document_loaders import TextLoader
from langchain_core.prompts import ChatPromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_bedrock_client():
    """
    Creates a Bedrock client for the Anthropic Claude model.
    """
    logging.info("Creating Bedrock client...")
    bedrock = boto3.client(service_name="bedrock-runtime")
    llm = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        client=bedrock,
        model_kwargs={
            "max_tokens": 4000,  # Generate up to 4000 tokens of output
            "temperature": 0.1,  # Generate deterministic responses
            "top_k": 250,        # Consider only the top 250 most likely tokens at each step
            "top_p": 1,          # Consider all tokens for generation (no cumulative probability limit)
            "stop_sequences": ["\n\nHuman"],  # Stop generating when encountering the sequence "\n\nHuman"
        }
    )
    logging.info("Bedrock client created successfully.")
    return llm

# Load the prompt json file 
logging.info("Loading prompt file...")
with open("prompts.json", 'r') as file:
    prompts = json.load(file)

def generate_notes(text, llm, prompt_subject):
    """
    Generates comprehensive notes from the given text using the provided language model (LLM).
    """
    logging.info(f"Generating notes using prompt '{prompt_subject}'...")
    prompt_template = prompts[prompt_subject]
    prompt = PromptTemplate.from_template(input_variable=['text'], template=prompt_template)
    chain = prompt | llm
    res = chain.invoke({'text': text})
    logging.info("Notes generated successfully.")
    return res.content


# Load the text you want to generate notes for
logging.info("Loading json file...")
with open("sample.json", 'r') as file:
    data = json.load(file)

# Create the Bedrock client
bedrock_llm = create_bedrock_client()

# Generate notes from the text
prompt_subject = "prompt_template1"  # Change this to the desired prompt subject
notes = generate_notes(data['text'], bedrock_llm, prompt_subject)
print(notes)