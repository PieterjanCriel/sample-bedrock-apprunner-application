# Foundation Models playground with AWS App Runner and AWS Bedrock

<img width="1003" alt="diagram_apprunner" src="https://github.com/PieterjanCriel/sample-bedrock-apprunner-application/assets/9216903/159b77bb-57d5-4f09-a695-ed7281a94b22">


This is a sample project to demonstrate how to use [AWS App Runner](https://aws.amazon.com/apprunner/) with [AWS Bedrock](https://aws.amazon.com/bedrock/) to deploy a minimalistic generative AI application.

The application itself transforms an email to a per person to-do list.
<img width="1601" alt="Screenshot 2023-10-29 at 19 23 31" src="https://github.com/PieterjanCriel/sample-bedrock-apprunner-application/assets/9216903/3e920dd8-8e1f-4165-b782-fda6d3a650fc">




## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template
* `cdk bootstrap`   bootstrap the AWS CDK toolkit
* `cdk destroy`     destroy the stack
