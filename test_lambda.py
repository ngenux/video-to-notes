import pytest
import json
from lambda_function import lambda_handler

def test_lambda_handler():
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
    result = lambda_handler(event,"s")
    assert result['statuscode'] == 200

    body = json.loads(result['body'])
    assert "The notes have been written to notes.md and uploaded to the S3 bucket" in body
