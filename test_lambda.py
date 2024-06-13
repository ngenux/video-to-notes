import unittest
from unittest.mock import patch, MagicMock
import json
from lambda_function import lambda_handler
import io

class TestLambdaHandler(unittest.TestCase):

    @patch('boto3.client')
    def test_lambda_handler_response(self, mock_boto_client):
        # Mock the S3 client
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        # Mock the S3 get_object response
        mock_s3.get_object.return_value = {
            'Body': io.StringIO(json.dumps({"text": "This is a test transcript."}))
        }

        # Mock the Bedrock runtime client response
        mock_bedrock_runtime = MagicMock()
        mock_boto_client.side_effect = [mock_s3, mock_bedrock_runtime]
        
        mock_bedrock_runtime.invoke_model.return_value = {
            'body': io.StringIO(json.dumps({
                "content": [
                    {
                        "text": "## Algebra\nExplain Algebra in detail.\n\n### Basic Formulas\nExplain the concept of basic formulas, provide examples, and illustrate how to solve relevant problems or equations.\nUse bullet points for clarity."
                    }
                ]
            }))
        }

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

        response = lambda_handler(event, "context")
        self.assertEqual(response['statuscode'], 200)

if __name__ == '__main__':
    unittest.main()
