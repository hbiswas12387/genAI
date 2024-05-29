import json
import boto3

# Note: This file is the lambda function which is created under AWS. This is just for representation.

# useful link : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html

#1.  below is to check that boto version should be greater than 1.28.63
print(boto3.__version__)  # the version is 1.34.42 so it's complaint 


#2. establish a client connection with bedrock..
client = boto3.client('bedrock-runtime')



def lambda_handler(event, context):

#3. Get user prompt via event, store that as variable and pass to the client body as prompt..

    print(event)
    user_prompt=event['prompt']

#4. Create a request syntax : Get request via console/prompt 

    response = client.invoke_model(
        body= json.dumps({"prompt": user_prompt,"temperature": 0.5,"max_tokens": 50}),
        contentType='application/json',
        accept='application/json',

        # using the cohere model below ( we can change it whatever model we want which we have access to)

        modelId='cohere.command-text-v14' 
        #modelId='ai21.j2-mid-v1'
    )

#5. Convert streaming body to byte and byte to java
    response_byte=response['body'].read()
    response_string=json.loads(response_byte)
    return response_string