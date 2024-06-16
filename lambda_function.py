import json
import boto3
import os
import io
import logging
import urllib
import botocore.exceptions
from dotenv import load_dotenv

load_dotenv()
# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
print("entered")
def initialize_s3_client():
    """
    Initialize the S3 client.
    
    Returns:
        boto3.client: S3 client instance.
    
    Example:
        >>> os.environ['AWS_ACCESS_KEY_ID'] = 'test_key'
        >>> os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret'
        >>> client = initialize_s3_client()
        >>> client.__class__.__name__ == 'S3'
        True
    """
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    return boto3.client('s3',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)

def get_transcript(s3_client, bucket_name, file_path):
    """
    Retrieve the transcript from S3.
    
    Args:
        s3_client (boto3.client): S3 client instance.
        bucket_name (str): Name of the S3 bucket.
        file_path (str): Path of the transcript file in the S3 bucket.
        
    Returns:
        str: Transcript text.
        
    Example:
        >>> s3_client = initialize_s3_client()
        >>> bucket_name = 'videos-summary'
        >>> file_path = 'Algebra Formulas/transcript.json'
        >>> s3_client.get_object = lambda Bucket, Key: {'Body': io.StringIO(json.dumps({'text': 'Sample text'}))}
        >>> get_transcript(s3_client, bucket_name, file_path)
        'Sample text'
    """
    s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
    transcript = json.load(s3_response['Body'])
    return transcript['text']

def define_prompt(transcript_text):
    """
    Define the prompt for the Bedrock API.
    
    Args:
        transcript_text (str): Transcript text.
        
    Returns:
        str: Formatted prompt.
        
    Example:
        >>> transcript_text = 'This is a sample transcript.'
        >>> prompt = define_prompt(transcript_text)
        >>> 'This is a sample transcript.' in prompt
        True
    """
    prompt = f"""
    As a professor, your task is to make notes for beginner students based on the given transcript.
    Identify the topics that are being taught and explain those topics from the given text.
    Ensure your notes are formatted using appropriate headings for each section and provide explanations for each sub-topic.
    Remember to separate the text from equations and provide examples and applications where applicable.
    Format the notes using Markdown MikTex LaTeX.
    
    Follow the structure provided below:
    
    ## [Identified Topic]
    Explain the Topic in detail.
    
    ### [Identified Sub-topic]
    Explain the concept of the sub-topic, provide examples, and illustrate how to solve relevant problems or equations.
    Use bullet points for clarity.
    
    Use the given example structure:
    
    Example structure:
    ## [Identified Topic]
    Explain the Topic in detail.
    
    ### [Identified Sub-topic]
    Explain the concept of the sub-topic, provide examples, and illustrate how to solve relevant problems or equations.
    In bullet format.
    
    Applications, if any, should be included in the text.
    
    Provide detailed explanations, examples, and step-by-step solutions where applicable.
    
    The transcript is provided below:
    {transcript_text}
    
    Let's work this out in a step by step way to be sure we have the right answer.
    """
    return prompt

def invoke_bedrock(bedrock_runtime, prompt):
    """
    Invoke the Bedrock API with the given prompt.
    
    Args:
        bedrock_runtime (boto3.client): Bedrock runtime client instance.
        prompt (str): Formatted prompt.
        
    Returns:
        str: Response text from the Bedrock API.
        
    Example:
        >>> bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        >>> prompt = 'This is a sample prompt.'
        >>> bedrock_runtime.invoke_model = lambda **kwargs: {'body': io.StringIO(json.dumps({'content': [{'text': 'Sample response'}]}))}
        >>> invoke_bedrock(bedrock_runtime, prompt)
        'Sample response'
    """
    messages = [{
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": prompt
            }
        ]
    }]
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "messages": messages
    })
    
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        contentType="application/json",
        accept="application/json",
        body=body
    )
    
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']

def upload_notes(s3_client, bucket_name, s3_notes_path, response_text):
    """
    Upload the notes to S3.
    
    Args:
        s3_client (boto3.client): S3 client instance.
        bucket_name (str): Name of the S3 bucket.
        s3_notes_path (str): Path to upload the notes file in the S3 bucket.
        response_text (str): Response text to upload.
        
    Example:
        >>> s3_client = initialize_s3_client()
        >>> bucket_name = 'videos-summary'
        >>> s3_notes_path = 'Algebra Formulas/notes.md'
        >>> response_text = 'Sample response text.'
        >>> s3_client.upload_fileobj = lambda *args, **kwargs: None
        >>> upload_notes(s3_client, bucket_name, s3_notes_path, response_text)
    """
    data = io.BytesIO(response_text.encode())
    s3_client.upload_fileobj(data, Bucket=bucket_name, Key=s3_notes_path)
    logger.info(f"The notes have been written to notes.md and uploaded to the S3 bucket '{bucket_name}' in path {s3_notes_path}.")
    print(f"The notes have been written to notes.md and uploaded to the S3 bucket '{bucket_name}' in path {s3_notes_path}.")

def lambda_handler(event, context):
    try:
        # Initialize the S3 client
        s3_client = initialize_s3_client()

        # Extract bucket name and file path from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_path = event['Records'][0]['s3']['object']['key']
        file_path = urllib.parse.unquote_plus(file_path, encoding='utf-8')

        logger.info(f'Bucket name: {bucket_name}')
        logger.info(f'File path: {file_path}')

        # Retrieve the transcript from S3
        transcript_text = get_transcript(s3_client, bucket_name, file_path)
        logger.info(f'Transcript text: {transcript_text}')

        # Define the prompt for the Bedrock API
        prompt = define_prompt(transcript_text)
        logger.info(f'Prompt: {prompt}')

        # Initialize the Bedrock runtime client
        bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

        # Invoke the Bedrock API
        response_text = invoke_bedrock(bedrock_runtime, prompt)
        logger.info(f'Response text: {response_text}')
        # Define the S3 path for the notes file
        s3_video_path = os.path.dirname(file_path)
        s3_notes_path = os.path.join(s3_video_path, 'notes.md')
        logger.info(f'S3 video path: {s3_video_path}')
        logger.info(f'S3 notes path: {s3_notes_path}')

        # Upload the notes to S3
        upload_notes(s3_client, bucket_name, s3_notes_path, response_text)
        logger.info(f"The notes have been written to notes.md and uploaded to the S3 bucket '{bucket_name}' in path {s3_notes_path}.")
        return {
            'statuscode': 200,
            'body': json.dumps(f"The notes have been written to notes.md and uploaded to the S3 bucket '{bucket_name}' in path {s3_notes_path}.")
        }
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        raise

# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()

event = {
    "Records": [
        {
            "s3": {
                "bucket": {
                    "name": "videos-summary" 
                },
                "object": {
                    "key": "Algebra Formulas/transcript.json"
                }
            }
        }
    ]
}

# testing CICD 123 

lambda_handler(event,"s")
