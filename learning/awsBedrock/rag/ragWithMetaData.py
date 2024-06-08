import boto3
import json
import base64
import os

# get current directory

modelArn = 'arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-premier-v1:0'

# Initialize the Bedrock client
client = boto3.client('bedrock-runtime')

# Read the CSV file from the local path
csv_file_path = '/Users/himanshubiswas/Downloads/test.csv'
with open(csv_file_path, 'rb') as file:
    csv_content = file.read()

# Encode the CSV content to base64
encoded_csv_content = base64.b64encode(csv_content).decode('utf-8')



# Define the external source configuration
external_sources_config = {
    'modelArn': modelArn,
    'sources': [
        {
            'byteContent': encoded_csv_content,
            'sourceType': "CSV"
        }
    ]
}

# Define the knowledge base source
knowledge_base_source = {
    'modelArn': modelArn,
    'knowledgeBaseId': '123456',
}


# Set up berock clients
client_bedrock_agent = boto3.client(service_name='bedrock-agent-runtime', region_name="us-east-1")



def retrieveAndGenerate(input):
    return client_bedrock_agent.retrieve_and_generate(
        input={
            'text': input
        },
        retrieveAndGenerateConfiguration={
            'externalSourcesConfiguration': external_sources_config,
            'knowledgeBaseConfiguration': knowledge_base_source,
            'type': 'EXTERNAL_SOURCES_AND_KNOWLEDGE_BASE'
    }            
        
)

response = retrieveAndGenerate("What is AWS?")#["output"]["text"]
print(response)


# # Make the request
# response = client.invoke_model(
#     modelId= 'amazon.titan-text-premier-v1:0',
#     contentType='application/json',
#     body=json.dumps(retrieve_and_generate_config)
# )

# # Print the response
# print(response['body'].read().decode('utf-8'))