#!/usr/bin/python

import os
from botocore.exceptions import ClientError
import boto3
from ansible.module_utils.basic import AnsibleModule
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview']
}

DOCUMENTATION = '''
---
module: ba_sts_assume_role
short_description: Assume a role using AWS Security Token Service and obtain temporary credentials

options:
  role_arn:
    description:
      - The Amazon Resource Name (ARN) of the role that the caller is assuming (http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_Identifiers.html#Identifiers_ARNs)
    required: true
  role_session_name:
    description:
      - Name of the role's session - will be used by CloudTrail
    required: true
  mfa_serial_number:
    description:
      - The identification number of the MFA device that is associated with the user who is making the AssumeRole call.
    required: false
    default: null
  mfa_token:
    description:
      - The value provided by the MFA device, if the trust policy of the role being assumed requires MFA.
    required: false
    default: null
  session_token:
   description:
      - the session token if you already solved the MFA challenge
    required: false
    default: null
'''


def run_module():
    args = dict(
        region=dict(required=False, default="us-east-1"),
        role_arn=dict(required=True, default=None),
        role_session_name=dict(required=True, default=None),
        mfa_serial_number=dict(required=False, default=None),
        mfa_token=dict(required=False, default=None),
        aws_access_key=dict(required=False, default=None),
        aws_secret_access_key=dict(required=False, default=None),
        aws_session_token=dict(required=False, default=None),
    )
    module = AnsibleModule(argument_spec=args, supports_check_mode=True)

    role_arn = module.params['role_arn']
    role_session_name = module.params['role_session_name']
    mfa_serial_number = module.params['mfa_serial_number']
    mfa_token = module.params['mfa_token']
    aws_access_key = module.params['aws_access_key']
    aws_secret_access_key = module.params['aws_secret_access_key']
    aws_session_token = module.params['aws_session_token']
    changed = False

    result = dict(
        changed=changed,
        sts_creds="",
        sts_user=""
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
        if aws_session_token:
            os.environ['AWS_SESSION_TOKEN'] = aws_session_token
            client = boto3.client('sts')
            res = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=role_session_name,
                DurationSeconds=3600
            )
        else:
            client = boto3.client('sts')
            res = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=role_session_name,
                DurationSeconds=3600,
                SerialNumber=mfa_serial_number,
                TokenCode=mfa_token
            )
        changed = True
    except Exception as e:
        
      clean_env()
      module.fail_json(mesg=str(e))

    result['changed'] = True
    result['sts_creds'] = res["Credentials"]
    result['sts_user'] = res["AssumedRoleUser"]

    clean_env()
    module.exit_json(**result)

def clean_env():
  del os.environ['AWS_ACCESS_KEY_ID']
  del os.environ['AWS_SECRET_ACCESS_KEY']
  del os.environ['AWS_SESSION_TOKEN']

def main():
    run_module()


if __name__ == '__main__':
    main()
