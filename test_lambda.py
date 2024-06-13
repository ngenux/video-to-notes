import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import lambda_handler
import io
import boto3  # Ensure boto3 is imported in your lambda_function.py

class TestLambdaHandler(unittest.TestCase):

    def setUp(self):
        # Create a mock S3 client
        self.mock_s3_client = MagicMock()

    @patch('boto3.client')
    def test_successful_processing(self, mock_boto_client):
        # Mock boto3.client to return the mock S3 client
        mock_boto_client.return_value = self.mock_s3_client

        # Define mock response from S3
        mock_s3_response = {
            'Body': io.BytesIO(json.dumps({"text": "This is a test transcript."}).encode())
        }
        self.mock_s3_client.get_object.return_value = mock_s3_response

        # Define mock response from Bedrock runtime client
        mock_bedrock_runtime = MagicMock()
        mock_boto_client.side_effect = [self.mock_s3_client, mock_bedrock_runtime]

        mock_bedrock_runtime.invoke_model.return_value = {
            'body': io.BytesIO(json.dumps({
                "content": [
                    {
                        "text": "## Algebra\nExplain Algebra in detail.\n\n### Basic Formulas\nExplain the concept of basic formulas, provide examples, and illustrate how to solve relevant problems or equations.\nUse bullet points for clarity."
                    }
                ]
            }).encode())
        }

        # Define the event for the Lambda handler
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

        # Call the Lambda handler function
        response = lambda_handler(event, "context")

        # Assertions
        self.assertEqual(response['statuscode'], 200)
        # Add more assertions as needed to verify the behavior of your Lambda handler

if __name__ == '__main__':
    unittest.main()
