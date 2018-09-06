# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file.
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#
# Description: This Lambda function sends an SNS notification to a given AWS SNS topic when an API call event by IAM root user is detected.
#              The SNS subject is- "API call-<insert call event> by Root user detected in Account-<insert account alias>, see message for further details". 
#              The JSON message body of the SNS notification contains the full event details.
# 
#
# Author: Sudhanshu Malhotra
# Updated:  Bob Peterson, Sungard Availability Services.
# Update to see if it shows up

import json
import boto3
import logging
import os
import botocore.session
import urllib2
from botocore.exceptions import ClientError
from CloudwatchLogAlert import CloudwatchLogger
session = botocore.session.get_session()

logging.basicConfig(level=logging.DEBUG)
logger=logging.getLogger(__name__)


def lambda_handler(event, context):
    #create alerter instance
    alerter=CloudwatchLogger()
    
    #SNS topic info
    snsARN = os.environ['SNSARN']          #Getting the SNS Topic ARN passed in by the environment variables.
    
    logger.setLevel(logging.DEBUG)
    
    logger.debug("Event is --- %s" %event)
    logger.debug("Context is --- %s" %context)
    
    
    #Extract details from event
    message = event
    consoleUrl = "https://console.aws.amazon.com/guardduty"
    finding =  message['detail']['type']
    findingTitle = message['detail']['title']
    #findingDescription =  message['detail']['']
    findingDescription =  message['detail']['description']
    findingTime =  message['detail']['updatedAt']
    account =  message['detail']['accountId']
    region =  message['detail']['region']
    messageId =  message['detail']['id']
    #lastSeen =  message['detail']['']
    if  message['detail']['severity'] < 4.0:
        severity = 'Low'
    elif message['detail']['severity'] < 7.0:
        severity = "Medium"
    else:
        severity = "High"
    
    
    snsclient = boto3.client('sns')

    

    #build message body
    subject = "GuardDuty Alert"
    message = ""+findingTitle+"\n\n"
    message = message+"Description:  " + findingDescription+"\n\n\n"
    message = message+"Severity:  "+severity+"\n\n"
    message = message+"Finding:  "+finding+"\n\n"
    message = message+"Account:  "+account+"\n\n"
    message = message+"Region:  "+region+"\n\n"
    message = message+"Last Seen:  "+findingTime+"\n\n"
    message = message+"Link:  "+consoleUrl+"/home?region="+region+"#/findings?search=id%3D"+messageId+"\n\n"
    message = message+"\n\n\n"
    message = message+ "##Event Details\n"+json.dumps(event, indent=4, sort_keys=True)
    
    #send SNS message
    try: 
        #Sending the notification...
        snspublish = snsclient.publish(
                        TargetArn= snsARN,
                        Subject=subject,
                        Message=json.dumps({'default':json.dumps(event),
                                            'email':message}),
                        MessageStructure='json')
        logger.debug("SNS publish response is-- %s" %snspublish)
    except ClientError as e:
        logger.error("An error occured: %s" %e)
    
    

    # Send alert to Cloudwatch log

    logMessage = {
        "awsid": event['account'],
        "region": event['region'],
        "subject": subject,
        "message": message,
        "sentBy": context.invoked_function_arn
      };
    
    alerter.logmessage(logMessage)
    