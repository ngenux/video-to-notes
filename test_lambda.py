import unittest
from unittest.mock import patch, MagicMock
import boto3
import os
import io
import json
from lambda_function import initialize_s3_client, lambda_handler, define_prompt, get_transcript, invoke_bedrock,upload_notes

class TestLambdaFunction(unittest.TestCase):

    @patch('boto3.client')
    def test_initialize_s3_client(self, mock_boto_client):
        client = initialize_s3_client()

        mock_boto_client.assert_called_with('s3')
        self.assertEqual(client, mock_boto_client.return_value)

    def test_define_prompt(self):
        transcript_text = 'Sample transcript text.'
        prompt = define_prompt(transcript_text)
        self.assertIn(transcript_text, prompt)

    @patch('boto3.client')
    def test_get_transcript(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        bucket_name = 'test_bucket'
        file_path = 'test_path/transcript.json'
        mock_body = MagicMock()
        mock_body.read.return_value = json.dumps({'text': 'Sample transcript'}).encode('utf-8')
        mock_s3_client.get_object.return_value = {'Body': mock_body}

        transcript = get_transcript(mock_s3_client, bucket_name, file_path)
        self.assertEqual(transcript, 'Sample transcript')
    
    @patch('boto3.client')
    def test_invoke_bedrock(self, mock_boto_client):
        mock_bedrock_runtime = MagicMock()
        mock_boto_client.return_value = mock_bedrock_runtime

        prompt = 'Sample prompt.'
        mock_response = {
            'content': [{'text': 'Sample response'}]
        }
        mock_bedrock_runtime.invoke_model.return_value = {'body': io.BytesIO(json.dumps(mock_response).encode())}

        response_text = invoke_bedrock(mock_bedrock_runtime, prompt)
        self.assertEqual(response_text, 'Sample response')
    
    @patch('boto3.client')
    def test_upload_notes(self, mock_boto_client):
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        bucket_name = 'test_bucket'
        s3_notes_path = 'test_path/notes.md'
        response_text = 'Sample response text.'

        upload_notes(mock_s3_client, bucket_name, s3_notes_path, response_text)
        mock_s3_client.upload_fileobj.assert_called_once()

    @patch('boto3.client')
    def test_lambda_handler_success(self, mock_boto_client):
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
        context = MagicMock()

        # Patch environment variables
        os.environ['AWS_ACCESS_KEY_ID'] = 'test_key'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret'

        # Mocking S3 client behavior
        mock_s3_client = MagicMock()
        mock_body = MagicMock()
        mock_body.read.return_value = b'{"text": "Sample transcript"}' 
        mock_s3_client.get_object.return_value = {'Body': mock_body}
        mock_boto_client.return_value = mock_s3_client
 
 
        # Mocking Bedrock runtime client behavior
        mock_bedrock_runtime = MagicMock()
        mock_response = MagicMock()
        mock_response.get.return_value = MagicMock()
        mock_response.get.return_value.read.return_value = json.dumps({
            "content": [{"text": "Sample response"}]
        }).encode('utf-8') 
        mock_bedrock_runtime.invoke_model.return_value = mock_response

        with patch('lambda_function.boto3.client', side_effect=[mock_s3_client, mock_bedrock_runtime]):
            result = lambda_handler(event, context)

        self.assertEqual(result['statuscode'], 200)
        self.assertIn('notes have been written to notes.md', result['body'])

if __name__ == '__main__':
    unittest.main()
