import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { join } from 'path';
import { DockerImageAsset, Platform } from 'aws-cdk-lib/aws-ecr-assets';
import { Effect, ManagedPolicy, PolicyStatement, Role, ServicePrincipal } from 'aws-cdk-lib/aws-iam';

import apprunner = require('@aws-cdk/aws-apprunner-alpha');


export class ApprunnerBedrockStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const password = process.env.PASSWORD;

    if (!password) {
        throw new Error('PASSWORD environment variable is required');
    }

    const image = new DockerImageAsset(this, 'DemoAppImage', {
        directory: join(__dirname, '..', 'app'),
        platform: Platform.LINUX_AMD64,
        buildArgs: {
            PASSWORD: password,
        },
        invalidation: {
            buildArgs: true,
        },
    });

    const instanceRole = new Role(this, 'DemoAppInstanceRole', {
        assumedBy: new ServicePrincipal('tasks.apprunner.amazonaws.com'),
    });

    const llmInvokeBedrockPolicyStatement = new PolicyStatement({
        effect: Effect.ALLOW,
        actions: ['bedrock:InvokeModel'],
        resources: ['arn:aws:bedrock:eu-central-1::foundation-model/anthropic.claude-instant-v1'],
    });

    instanceRole.addToPolicy(llmInvokeBedrockPolicyStatement);

    instanceRole.addManagedPolicy(ManagedPolicy.fromAwsManagedPolicyName('AmazonSageMakerFullAccess'));

    new apprunner.Service(this, 'DemoApp', {
        source: apprunner.Source.fromAsset({
            imageConfiguration: { port: 8080 },
            asset: image,
        }),
        instanceRole: instanceRole,
    });
  }
}
