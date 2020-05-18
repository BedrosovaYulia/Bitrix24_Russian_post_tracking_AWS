# Bitrix24_Russian_post_tracking
 Cloud Bitrix24 and Post Tracking - SOAP Integration via AWS Lambda.
 Detailed project description in the blog: http://bedrosovayulia.blogspot.com/2019/07/cloud-bitrix24-and-post-tracking-soap.html
 
 What do we need to do for the intergation:
1) Get the login and the password for integration on the Russian Post website: https://www.pochta.ru/support/business/api

2) Prepare a Lambda Layer with a library for working with SOAP. I chose the open-source Zeep library. http://bedrosovayulia.blogspot.com/2019/07/how-to-reate-aws-lambda-layer-with-zeep.html

3) On the side of Bitrix24, we need to create an inbound webhook with the right to send messages and with access to the universal lists (in my case) or, perhaps, to CRM - depending on where you need to save the checking result.

 4) Write a business process in Bitrix24, which will call the outbound webhook, giving it the post tracking number, as well as the ID of the element and information block, in which the result of the check must be saved.

 5) Write an AWS Lambda function that gets data from Bitrix24, requests the status of the tracking number from Post SOAP service and return the result to Bitrix24 via the inbound webhook.

 6) Configure the API Gateway for our Lambda function. I described this process in detail earlier in my blog: http://bedrosovayulia.blogspot.com/2019/07/aws-lambda-and-api-gateway-for-bitrix24.html

