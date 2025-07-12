#!/usr/bin/env python3
import os
import aws_cdk as cdk
from yc_coach.yc_coach_stack import YcCoachStack

app = cdk.App()
YcCoachStack(app, "YcCoachStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION', 'us-east-1')
    )
)

app.synth()
