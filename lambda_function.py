import json
import boto3
import pandas as pd

s3 = boto3.client('s3')
sns = boto3.client('sns')

def lambda_handler(event, context):
    try:
        # Check if 'Records' key exists in the event
        if 'Records' in event:
            for record in event['Records']:
                # Extract bucket name and key from the event
                bucket = record['s3']['bucket']['name']
                key = record['s3']['object']['key']
                
                # Read JSON file into DataFrame
                obj = s3.get_object(Bucket=bucket, Key=key)
                df = pd.read_json(obj['Body'])
                
                # Filter records where status is 'delivered'
                filtered_df = df[df['status'] == 'delivered']
                
                # Write filtered DataFrame to a new JSON file in doordash-target-zn
                target_bucket = 'doordash-target-zn'
                target_key = key.replace('landing', 'target')
                s3.put_object(Bucket=target_bucket, Key=target_key, Body=filtered_df.to_json(orient='records'))
                
                # Publish success message to SNS topic
                sns.publish(TopicArn='arn:aws:sns:us-east-1:843334912286:GrowDataSkills', Message='Data processed successfully')
        else:
            # If 'Records' key is missing, raise an error
            raise KeyError("'Records' key not found in event data")
    except Exception as e:
        # Publish failure message to SNS topic
        sns.publish(TopicArn='arn:aws:sns:us-east-1:843334912286:GrowDataSkills', Message=f'Error processing data: {str(e)}')
        raise e  # Re-raise the exception for Lambda error handling
