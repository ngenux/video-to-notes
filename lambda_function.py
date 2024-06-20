import json
import boto3
import os
import io
import logging
import urllib

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # Initialize the S3 client
        s3_client = boto3.client('s3')

        # Extract bucket name and file path from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_path = event['Records'][0]['s3']['object']['key']
        file_path = urllib.parse.unquote_plus(file_path, encoding='utf-8')

        logger.info(f'Bucket name: {bucket_name}')
        logger.info(f'File path: {file_path}')

        # Retrieve the transcript from S3
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
        transcript = json.load(s3_response['Body'])
        transcript_text = transcript['text']
        logger.info(f'Transcript text: {transcript_text}')

        # Initialize the Bedrock runtime client
        bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

        # Define the prompt for the Bedrock API
        prompt = f"""
         Human: You are a Professor, who is tasked with making notes for students who are beginners.
        Identify the topics that are being taught and explain those topics from the given text below.
        Here is the text to create notes.
        text = {transcript_text}

        Format your notes using appropriate headings for each section and provide explanations for each sub-topic.
        Remove all the preambles in the notes.
        Separate text from equations.
        Use .md Markdown MikTex latex format for the notes.

        # Example structure:

        ## Identified Topic
        Explain the Topic in detail. 

        ### Identified Sub-topic
        Explain the concept of the sub-topic, provide examples, and illustrate how to solve relevant problems or equations.
        In bullet format

        Give the applications if any present in text.
       
        Provide detailed explanations, examples, and step-by-step solutions where applicable.

        Assistant:
        """
        logger.info(f'Prompt: {prompt}')

        # Define the messages payload for the Bedrock API
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]

        # Define the request body for the Bedrock API
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10000,
            "messages": messages
        })

        try:
            # Invoke the Bedrock API
            response = bedrock_runtime.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                contentType="application/json",
                accept="application/json",
                body=body
            )
        except botocore.exceptions.BotoCoreError as e:
            logger.error(f"Error invoking Bedrock API: {e}")
            raise

        # Parse the response from the Bedrock API
        response_body = json.loads(response.get('body').read())
        response_text = response_body['content'][0]['text']
        logger.info(f'Response text: {response_text}')

        # Define the S3 path for the notes file
        s3_video_path = os.path.dirname(file_path)
        s3_notes_path = os.path.join(s3_video_path, 'notes.md')
        logger.info(f'S3 video path: {s3_video_path}')
        logger.info(f'S3 notes path: {s3_notes_path}')

        # Upload the notes to S3
        data = io.BytesIO(response_text.encode())
        s3_client.upload_fileobj(data, Bucket=bucket_name, Key=s3_notes_path)
        logger.info(f"The notes have been written to notes.md and uploaded to the S3 bucket '{bucket_name}' in path {s3_notes_path}.")

    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        raise
