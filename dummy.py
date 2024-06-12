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
      print(f"Error downloading file: {e}")
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
    You are a Professor, who is tasked to make note for student who is beginner.
    Identify the topics that are being taught, explain about those topics form the given text below : {csv_content}
    
    Format your notes using appropriate headings for each section and explation about sub_topic .
    Don't plot any graph.
    Seperate text from equations.
    Give notes in .md LaTex format.
    """
    prompt = PromptTemplate.from_template(input_variable=['csv_content'] ,template=prompt_template)
    
    chain = prompt | llm
    
    res = chain.invoke({'csv_content':csv_content})


    print(res.content,"?????????????????????????????????????????????????????????????????????")
    return {
        'statusCode': 200,
        'body': json.dumps(res.content)
    }

event = {
  "bucket_name": "videos-summary",
  "key": "Algebra Formulas/transcript.json"
}

lambda_handler(event, "s")