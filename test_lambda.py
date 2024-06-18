import unittest
from unittest.mock import patch, MagicMock
import boto3
import os
import json
from lambda_function import initialize_s3_client, lambda_handler

class TestLambdaFunction(unittest.TestCase):

    # @patch('boto3.client')
    # def test_initialize_s3_client(self, mock_boto_client):
    #     # Patch environment variables
    #     os.environ['AWS_ACCESS_KEY_ID'] = 'test_key'
    #     os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret'
    #     client = initialize_s3_client()

    #     mock_boto_client.assert_called_with(
    #         's3',
    #         aws_access_key_id='test_key',
    #         aws_secret_access_key='test_secret'
    #     )
    #     self.assertEqual(client, mock_boto_client.return_value)

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
            print(result,"//////////////////////////////////////////////")

        # Assertions
        self.assertEqual(result['statuscode'], 200)
        self.assertIn('notes have been written to notes.md', result['body'])

if __name__ == '__main__':
    unittest.main()
