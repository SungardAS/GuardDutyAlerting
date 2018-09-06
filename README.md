
# GuardDuty Alerting Example

Creates a capability to monitor GuardDuty findings and sent alerts.

![Sample Alert Flow](/docs/images/GuardDuty%20Alerting%20Flow.png)



## Installation Options

- [Prerequisites](#prerequisites-for-setup)
- [CloudFormation](#setup-using-cloudformation) - Setup dedicated Stack with CloudFormation.  Code is not auto-updated.

## Prerequisites For Setup


### Alert Log Destination

If this project is deployed in an account that is different from the main account where the Alert System was deployed, we need to add a permission for the account to access the Destination in the main account.

  - Go to the Lambda console of the main account and in the ‘us-east-1’ region

  - Find a function called ‘SungardAS-Alerts- Permission-xxxx’ and configure the test event as below:

  ```javascript
  {
      "region": "<region name where this project is deployed>",
      "account": "<account number where this project is deployed>",
      "destinationName": "<destination name defined in main Alert System; 'alertDestination' if not changed>"
  }
  ```

  - Run Test to execute this lambda function



## Setup using CloudFormation

### Prep Lambda Code

1. Create a ZIP file of the source code files in "src" directory.  The files should be in the root of the zip file.

2. Upload the file to your favorite S3 bucket


### Crate CloudFormation Stack

Create a Cloudformation stack using 'GuardDutyMonitor.yaml' using below input values

Input Parameter Values

- CreateCloudWatchSubscription:

  Select "Yes" to create a CloudWatch Subscription to send alerts to an alerting account.  Select "No" if you do not want to enable the Subscription.
  
- CloudWatchLogDestinationArn:

  ARN of Cloudwatch Log in remote account where Cloudwatch log subscription will send log info.

- CloudWatchLogGroupName:

  Name of a local Cloudwatch Log Group where this trigger sends alert messages

- LambdaTimeout

  Enter a timeout value in seconds for the lambda function. Min is 3, max is 300 and default is 60.

- LambdaS3Bucket:

  Name of the S3 bucket where the lambda function is stored

- LambdaS3Key:

  Name of the S3 key of the Lambda function (include the prefix as well)






## [![Sungard Availability Services | Labs][labs-logo]][labs-github-url]

This project is maintained by the Labs group at [Sungard Availability
Services](http://sungardas.com)

GitHub: [https://sungardas.github.io](https://sungardas.github.io)

Blog:
[http://blog.sungardas.com/CTOLabs/](http://blog.sungardas.com/CTOLabs/)

[labs-github-url]: https://sungardas.github.io
[labs-logo]: https://raw.githubusercontent.com/SungardAS/repo-assets/master/images/logos/sungardas-labs-logo-small.png
[aws-services-image]: ./docs/images/logo.png?raw=true
