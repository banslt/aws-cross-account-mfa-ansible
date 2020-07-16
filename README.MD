# Ansible AWS multi account jump with one time mfa challenge using Boto3


# How to use:

1. Move these python modules in your ansible modules path *(should be something like venvs/ansible-env/lib/python3.7/site-packages/ansible/modules/)*

2. Use it in your playbook:

### main.yml :
```
---
- name: AWS Deploy
  hosts: localhost
  gather_facts: false
  vars_files:
    - vars/sts.yml
  tasks:
    - name: AWS Give my token plzzzzz
      ba_get_session_token:
        mfa_serial_number: "{{sts_mfa | default(omit)}}"
        mfa_token: "{{sts_mfatoken | default(omit)}}"
      register: temp_cred
      when: sts

    - name: Retrieve STS Credentials For Jump from Dev Acc to Prod
      set_fact:
        sts_jump_aws_access_key: "{{ hostvars['localhost']['temp_cred'].sts_creds.AccessKeyId }}"
        sts_jump_aws_secret_key: "{{ hostvars['localhost']['temp_cred'].sts_creds.SecretAccessKey }}"
        sts_jump_session_token: "{{ hostvars['localhost']['temp_cred'].sts_creds.SessionToken }}"
      when: sts

    - name: List buckets from Dev Acc
      shell: >
        aws s3api list-buckets
      environment:
        AWS_ACCESS_KEY_ID: "{{ sts_jump_aws_access_key }}"
        AWS_SECRET_ACCESS_KEY: "{{ sts_jump_aws_secret_key }}"
        AWS_SESSION_TOKEN: "{{ sts_jump_session_token }}"
      args:
        executable: /bin/bash

    - name: AWS Assume Role
      ba_sts_assume_role:
        role_arn: "{{sts_role_arn}}"
        role_session_name: "{{sts_role_session_name}}"
        aws_access_key: "{{sts_jump_aws_access_key}}"
        aws_secret_access_key: "{{sts_jump_aws_secret_key}}"
        aws_session_token: "{{sts_jump_session_token}}"
      register: assumed_role
      when: sts

    - name: Retrieve STS Credentials for S3 on Prod Acc
      set_fact:
        sts_aws_access_key: "{{ hostvars['localhost']['assumed_role'].sts_creds.AccessKeyId }}"
        sts_aws_secret_key: "{{ hostvars['localhost']['assumed_role'].sts_creds.SecretAccessKey }}"
        sts_session_token: "{{ hostvars['localhost']['assumed_role'].sts_creds.SessionToken }}"
      when: sts

    - name: List buckets from Prod Acc
      shell: >
        aws s3api list-buckets
      environment:
        AWS_ACCESS_KEY_ID: "{{ sts_aws_access_key }}"
        AWS_SECRET_ACCESS_KEY: "{{ sts_aws_secret_key }}"
        AWS_SESSION_TOKEN: "{{ sts_session_token }}"
      args:
        executable: /bin/bash
```


### vars/sts.yml :

```
---
sts: true
sts_role_arn: "arn:aws:iam::DESTINATIONACCOUNTID:role/ROLE" # Role ARN for Destination Assumed Role
sts_mfa: "arn:aws:iam::JUMPACCOUNTID:mfa/USER" # MFA Serial of jump account
sts_role_session_name: "ansible" # The session name you will use (for CloudTrail)
```

3. Invoke the playbook :   `ansible-playbook main.yml -e sts_mfatoken=012345 -vvv`
