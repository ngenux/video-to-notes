import json
import boto3
import pytest
from moto import mock_aws   
import lambda_function
from unittest import mock
import io

@pytest.fixture
def s3_setup():
    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='videos-summary')
        s3.put_object(Bucket='videos-summary', Key='Algebra Formulas/transcript.json', Body=json.dumps({"text": "Sample transcript text"}))
        yield

@pytest.fixture
def mock_bedrock_runtime(mocker):
    mock_client = mocker.patch('boto3.client')
    
    mock_bedrock_runtime = mock.Mock()
    mock_bedrock_response = {
        'body': io.BytesIO(json.dumps({
            "content": [{
                "text": "## Sample Topic\n### Sample Sub-topic\nSample notes content."
            }]
        }).encode('utf-8'))
    }
    mock_bedrock_runtime.invoke_model.return_value = mock_bedrock_response

    mock_client.return_value = mock_bedrock_runtime
    return mock_bedrock_runtime

def test_lambda_handler_success(s3_setup, mock_bedrock_runtime, mocker):
    s3_client = boto3.client('s3')

    # Mock S3 get_object to return a proper response object
    s3_response = {
        'Body': io.BytesIO(json.dumps({"text": "Sample transcript text"}).encode('utf-8'))
    }
    mocker.patch.object(s3_client, 'get_object', return_value=s3_response)
    
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

    lambda_function.lambda_handler(event, "s")

    result = s3_client.get_object(Bucket='videos-summary', Key='Algebra Formulas/notes.md')
    notes_content = result['Body'].read().decode('utf-8')
    print(notes_content,"//////////////////////////")

    assert "## Sample Topic" in notes_content
    assert "### Sample Sub-topic" in notes_content
    assert "Sample notes content." in notes_content
