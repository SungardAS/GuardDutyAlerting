from __future__ import print_function
import boto3
import json
import logging
import os
import botocore.session
from datetime import datetime
from calendar import timegm
import sys
from botocore.exceptions import ClientError


class CloudwatchLogger(object):

    def __init__(self):
        #Setup Log and log stream name 
        #   Log stream is based on date (YYYY/MM/DD)
        #   (TBD - read env variable for log name)
        #self.log_group="EventLogTest"
        self.log_group=os.environ['CLOUDWATCHLOGNAME']
        self.logdate=datetime.now().strftime('%Y/%m/%d')
        print(self.log_group)

        # setup Cloudwatch Logs (CWL) client
        self.cwl_client = boto3.client('logs')
        #cwl_client.describe_log_groups()


    #Create timestamp in milliseconds since Unix Epoch
    def unix_time(self,dttm=None):
        if dttm is None:
           dttm = datetime.utcnow()
        
        return timegm(dttm.utctimetuple())*1000


    def logmessage(self,logMessage):
        #cwl_client.describe_log_groups(logGroupNamePrefix=self.log_group)


        sequenceToken=None

        logstreams=self.cwl_client.describe_log_streams(logGroupName=self.log_group,logStreamNamePrefix=self.logdate)
        #print(logstreams)

        # Create new log stream if it does not exist
        if len(logstreams['logStreams']) == 0:
            clsresponse=self.cwl_client.create_log_stream(logGroupName=self.log_group,logStreamName=self.logdate)
            print(clsresponse)
        else:
            sequenceToken=logstreams['logStreams'][0]['uploadSequenceToken']


        # Append current time to message

        sentAt = datetime.utcnow().isoformat()
        logMessage['sentAt']=sentAt

        logEvents=[
                {
                    'timestamp': self.unix_time(),
                    'message': json.dumps(logMessage)
                },
            ]

        #Build arguments to pass to put_log_events API call.
        kwargs = dict(logGroupName=self.log_group, logStreamName=self.logdate,
                      logEvents=logEvents)

        # Add sequence number if we have it
        if sequenceToken is not None:
            kwargs["sequenceToken"] = sequenceToken

        try:
            response = self.cwl_client.put_log_events(**kwargs)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") in ("DataAlreadyAcceptedException",
                                                           "InvalidSequenceTokenException"):
                kwargs["sequenceToken"] = e.response["Error"]["Message"].rsplit(" ", 1)[-1]
                response = self.cwl_client.put_log_events(**kwargs)
            else:
                raise
                
        return

