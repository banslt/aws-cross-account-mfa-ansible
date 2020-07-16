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
module: ba_get_session_token
short_description: Get Session token and temp creds

options:
  mfa_serial_number:
    description:
      - he identification number of the MFA device that is associated with the user who is making the AssumeRole call.
    required: false
    default: null
  mfa_token:
    description:
      - The value provided by the MFA device, if the trust policy of the role being assumed requires MFA.
    required: false
    default: null
'''


def run_module():
    args = dict(
        mfa_serial_number=dict(required=False, default=None),
        mfa_token=dict(required=False, default=None),
    )
    module = AnsibleModule(argument_spec=args, supports_check_mode=True)

    mfa_serial_number = module.params['mfa_serial_number']
    mfa_token = module.params['mfa_token']
    changed = False

    result = dict(
        changed=changed,
        sts_creds=""
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        client = boto3.client('sts')
        res = client.get_session_token(
            DurationSeconds=3600,
            SerialNumber=mfa_serial_number,
            TokenCode=mfa_token
        )
        changed = True
    except Exception as e:
        module.fail_json(mesg=str(e))

    result['changed'] = True
    result['sts_creds'] = res["Credentials"]

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
