# import unittest
# from unittest.mock import patch, MagicMock
# import json
# import io
# import os
# from dtest import (
#     initialize_s3_client,
#     get_transcript,
#     define_prompt,
#     invoke_bedrock,
#     upload_notes,
#     lambda_handler
# )

# class TestLambdaFunction(unittest.TestCase):
    
#     @patch('boto3.client')
#     def test_initialize_s3_client(self, mock_boto_client):
#         os.environ['AWS_ACCESS_KEY_ID'] = 'test_key'
#         os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret'
        
#         client = initialize_s3_client()
        
#         mock_boto_client.assert_called_with(
#             's3',
#             aws_access_key_id='test_key',
#             aws_secret_access_key='test_secret'
#         )
#         self.assertEqual(client, mock_boto_client.return_value)
    
#     @patch('boto3.client')
#     def test_get_transcript(self, mock_boto_client):
#         s3_client = mock_boto_client.return_value
#         s3_client.get_object.return_value = {'Body': io.StringIO(json.dumps({'text': 'Sample text'}))}
        
#         bucket_name = 'videos-summary'
#         file_path = 'Algebra Formulas/transcript.json'
        
#         transcript = get_transcript(s3_client, bucket_name, file_path)
        
#         s3_client.get_object.assert_called_with(Bucket=bucket_name, Key=file_path)
#         self.assertEqual(transcript, 'Sample text')
    
#     def test_define_prompt(self):
#         transcript_text = 'This is a sample transcript.'
#         prompt = define_prompt(transcript_text)
        
#         self.assertIn('This is a sample transcript.', prompt)
#         self.assertIn('## [Identified Topic]', prompt)
#         self.assertIn('### [Identified Sub-topic]', prompt)
    
#     @patch('boto3.client')
#     @patch('json.loads')
#     def test_invoke_bedrock(self, mock_json_loads, mock_boto_client):
#         bedrock_runtime = mock_boto_client.return_value
#         mock_json_loads.return_value = {'content': [{'text': 'Sample response'}]}
        
#         prompt = 'This is a sample prompt.'
        
#         response_text = invoke_bedrock(bedrock_runtime, prompt)
        
#         bedrock_runtime.invoke_model.assert_called_once()
#         self.assertEqual(response_text, 'Sample response')
    
#     @patch('boto3.client')
#     def test_upload_notes(self, mock_boto_client):
#         s3_client = mock_boto_client.return_value
#         bucket_name = 'videos-summary'
#         s3_notes_path = 'Algebra Formulas/notes.md'
#         response_text = 'Sample response text.'
        
#         upload_notes(s3_client, bucket_name, s3_notes_path, response_text)
        
#         s3_client.upload_fileobj.assert_called_once()
    
#     @patch('boto3.client')
#     @patch('lambda_function.upload_notes')
#     @patch('lambda_function.invoke_bedrock')
#     @patch('lambda_function.define_prompt')
#     @patch('lambda_function.get_transcript')
#     def test_lambda_handler(self, mock_get_transcript, mock_define_prompt, mock_invoke_bedrock, mock_upload_notes, mock_boto_client):
#         event = {
#             "Records": [
#                 {
#                     "s3": {
#                         "bucket": {
#                             "name": "videos-summary"
#                         },
#                         "object": {
#                             "key": "Algebra Formulas/transcript.json"
#                         }
#                     }
#                 }
#             ]
#         }
        
#         context = None
        
#         mock_get_transcript.return_value = 'Sample transcript text.'
#         mock_define_prompt.return_value = 'Sample prompt.'
#         mock_invoke_bedrock.return_value = 'Sample response text.'
        
#         response = lambda_handler(event, context)
        
#         self.assertEqual(response['statuscode'], 200)
#         self.assertIn('The notes have been written to notes.md', response['body'])
#         mock_get_transcript.assert_called_once()
#         mock_define_prompt.assert_called_once()
#         mock_invoke_bedrock.assert_called_once()
#         mock_upload_notes.assert_called_once()

# if __name__ == '__main__':
#     unittest.main()


import unittest
from unittest.mock import patch, MagicMock
import boto3
import os
from dtest import initialize_s3_client

class TestLambdaFunction(unittest.TestCase):

    @patch('boto3.client')
    def test_initialize_s3_client(self, mock_boto_client):
        # Patch environment variables
        with patch.dict(os.environ, {'KEY': 'test_key', 'S_KEY': 'test_secret'}):
            client = initialize_s3_client()

            mock_boto_client.assert_called_with(
                's3',
                aws_access_key_id='test_key',
                aws_secret_access_key='test_secret'
            )
            self.assertEqual(client, mock_boto_client.return_value)

if __name__ == '__main__':
    unittest.main()
