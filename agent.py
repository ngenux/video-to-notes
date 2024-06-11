# physics_keywords = ["force", "energy", "mechanics", "equation"]
# math_keywords = ["solve", "formula", "theorem", "proof"]

# # Subject identification function
# def identify_subject(transcript):
#   """
#   This function analyzes the transcript for subject keywords.
#   """
#   transcript_words = transcript.lower().split()
#   physics_count = sum(word in physics_keywords for word in transcript_words)
#   math_count = sum(word in math_keywords for word in transcript_words)
#   if physics_count > math_count:
#     return "physics"
#   elif math_count > physics_count:
#     return "mathematics"
#   else:
#     return "unknown"

# # Prompt generation function
# def generate_prompt(subject):
#   """
#   This function generates a prompt based on the identified subject.
#   """
#   prompts = {
#       "physics": "Focus on key concepts like forces, energy, or mechanics. Identify equations and important results.",
#       "mathematics": "Pay attention to problem-solving steps, formulas used, and theorems mentioned."
#   }
#   return prompts.get(subject, "Use a general note-taking strategy.") 

# transcript = "Gravitational force waves, predicted by Einstein’s theory of general relativity, are ripples in spacetime caused by massive objects in motion. These waves carry information about cosmic events (like black hole mergers) and allow us to study the universe in new ways. Their detection by instruments like LIGO has revolutionized gravitational wave astronomy"
# subject = identify_subject(transcript)
# prompt = generate_prompt(subject)

# print(f"Transcript Subject: {subject}")
# print(f"Prompt for Note-Taking: {prompt}")


import boto3
from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate
from langchain.docstore.document import Document
from langchain_aws import BedrockLLM, ChatBedrock
from langchain_community.chat_models import BedrockChat
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RefineDocumentsChain, LLMChain
from langchain_core.prompts import ChatPromptTemplate
import json
from langchain_community.chat_models import BedrockChat

def lambda_handler(event, context):
    s3 = boto3.client('s3')

    bucket_name = event['bucket_name']
    key = event['key']

    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        csv_content = response['Body'].read().decode('utf-8')
    except Exception as e:
      return {
            'statusCode': 404,
            'body': json.dumps(f"Unable to find the S3 file at {key}: {e}")
        }
    bedrock=boto3.client(service_name="bedrock-runtime")
    llm=ChatBedrock(model_id="anthropic.claude-3-sonnet-20240229-v1:0",client=bedrock,
                 model_kwargs = {
                     "max_tokens": 4000,
                     "temperature": 0.1,
                     "top_k": 250,
                     "top_p": 1,   
                     "stop_sequences": ["\n\nHuman"],
                     })
    prompt_template = """
    You are an intelligent assistant. 
    Your task is to analyze the provided transcript and identify the primary subject mentioned in it. 
    Focus on identifying subjects related to Physics, Chemistry, Mathematics, or Statistics. 

    Here is the transcript:
    {{csv_content}}

    Please output only the primary subject name, which should be one of the following:
    - Physics
    - Chemistry
    - Mathematics
    - Statistics

    If none of these subjects are mentioned, respond with what subject you feel it.

    Subject:
    """
    prompt = PromptTemplate.from_template(input_variable=['csv_content'] ,template=prompt_template)
    
    chain = prompt | llm
    
    res = chain.invoke({'csv_content':csv_content})
    print(res.content)
    prompt_to_be_selected = res.content
    prompts = {
    "Physics": "physics prompt.",
    "mathematics": "Mathematics prompt."
    }
    # check for prompt availability and select prompt
    if prompt_to_be_selected in prompts:
      selected_prompt = prompts[prompt_to_be_selected]
      print(f"Selected Prompt: {selected_prompt}")
      return selected_prompt
    else:
      print(f"Prompt '{prompt_to_be_selected}' not found in prompts.")
       
    return {
        'statusCode': 200,
        'body': json.dumps('json.dumps(f"subject"{res.content}')
    }

event = {
  "bucket_name": "videos-summary",
  "key": "Algebra Formulas/transcript.json"
}

lambda_handler(event, "s")



