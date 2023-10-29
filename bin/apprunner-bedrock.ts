#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ApprunnerBedrockStack } from '../lib/apprunner-bedrock-stack';

const app = new cdk.App();

new ApprunnerBedrockStack(app, 'ApprunnerBedrockStack', {});