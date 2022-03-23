import boto3
sns = boto3.client("sns", 
                region_name="ap-south-1", 
                aws_access_key_id="AKIAXPHB5CHQTA2HSLM3", 
                aws_secret_access_key="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")

def send_sms(number, message, sender_name):
    sns.publish(
        PhoneNumber=number, 
        Message=message,
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': sender_name,
            }
        },
    )