import unittest
from lambda_function import lambda_handler

class TestLambdaHandler(unittest.TestCase):

    def test_lambda_handler_response(self):
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

