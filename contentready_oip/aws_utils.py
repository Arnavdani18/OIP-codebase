import boto3
import frappe

def send_sms(number, message):
    if not number.startswith("+") and not number.startswith("00"):
        number = "+91" + number
    sns = boto3.client("sns", 
                region_name="ap-south-1", 
                aws_access_key_id=frappe.get_value("OIP Configuration", "", "aws_key"), 
                aws_secret_access_key=frappe.get_value("OIP Configuration", "", "aws_secret"))
    sns.publish(
        PhoneNumber=number, 
        Message=message,
        MessageAttributes={
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': frappe.get_value("OIP Configuration", "", "sender_name"),
            }
        },
    )