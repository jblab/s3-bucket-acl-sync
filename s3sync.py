#!/usr/bin/python3
"""s3sync.py: Sync files between s3 buckets."""
__author__ = "Julien Bonnier"
__copyright__ = "Copyright 2019, Jblab"
__credits__ = ["Julien Bonnier"]
__license__ = "Apache License, Version 2.0"
__version__ = "0.1.0"
__maintainer__ = "Julien Bonnier"
__email__ = "no-reply@julienbonnier.com"
__status__ = "Stable"

import boto3
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Sync files between s3 buckets.')
    parser.add_argument(
        '-K', '--key',
        help='AWS access key id, this has precedence over --profile option.'
    )
    parser.add_argument(
        '-S', '--secret',
        help='AWS secret acces key.'
    )
    parser.add_argument(
        '-s', '--src', metavar='BUCKET',
        help='Source S3 bucket name.'
    )
    parser.add_argument(
        '-d', '--dst', metavar='BUCKET',
        help='Destination S3 bucket name.'
    )
    parser.add_argument(
        '-P', '--profile', default='default',
        help='AWS profile to use.'
    )
    parser.add_argument(
        '--dryrun', action='store_true', default=False,
        help='Displays the operations that would be performed using the ' + \
             'specified command without actually running them.'
    )
    parser.add_argument(
        '--list', action='store_true', default=False,
        help='Only lists files in source and/or destination bucket(s).'
    )
    parser.add_argument(
        '--get-policy', action='store_true', default=False,
        help='Prints out the policy required in the source bucket to ' + \
             'allow the copy across AWS accounts.'
    )
    parser.add_argument(
        '--skip-existing', action='store_true', default=False,
        help='Skips existing key names, does not check that files are the same.'
    )

    args = parser.parse_args()

    # Setting the variable based on input args
    src_bucket = args.src
    dst_bucket = args.dst

    # Starting a boto3 session
    try:
        if args.key is not None or args.secret is not None:
            if args.key is None or args.secret is None:
                sys.exit('Error, arguments key and secret must come in pairs.')
            session = boto3.Session(
                aws_access_key_id=args.key,
                aws_secret_access_key=args.key
            )
        elif args.profile is not None:
            session = boto3.Session(profile_name=args.profile)
        else:
            session = boto3.Session()
    except Exception as e:
        sys.exit(e)

    # Creating a s3 resource
    s3 = session.resource('s3')

    # List bucket(s)
    if args.list:
        if src_bucket is not None:
            list_bucket(src_bucket, s3)
        if dst_bucket is not None:
            list_bucket(dst_bucket, s3)
        sys.exit()

    if src_bucket is None or dst_bucket is None:
        sys.exit('Error, you must specify a source and a destination bucket.')

    # Print policy
    if args.get_policy:
        user_arn = session.resource('iam').CurrentUser().arn
        print_policy(src_bucket, user_arn)

    # Sync buckets
    copy_bucket(src_bucket, dst_bucket, s3, args.dryrun, args.skip_existing)


def list_bucket(bucket_name, s3):
    try:
        bucket = s3.Bucket(name=bucket_name)

        print('\nListing objects in the {:s} bucket.\n'.format(bucket_name))

        batch = []
        for obj in bucket.objects.all():
            batch.append('{:s} ({:s})'.format(obj.key, get_canned_acl(obj)))
            if len(batch) == 10:
                print('\n'.join(batch))
                batch = []
        if len(batch) > 0:
            print('\n'.join(batch))
    except Exception as e:
        print(e)


def get_canned_acl(obj):
    acl = obj.Acl().grants
    public = []
    for grant in acl:
        grantee = grant.get('Grantee')
        if grantee.get('Type') == 'Group' and grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
            public.append(grant.get('Permission'))

    if 'READ' in public and 'WRITE' in public:
        return 'public-read-write'
    elif 'READ' in public:
        return 'public-read'
    elif 'WRITE' in public:
        return 'public-write'
    else:
        return 'private'


def copy_bucket(src_bucket, dst_bucket, s3, dryrun=False, skip_existing=False):
    src = s3.Bucket(src_bucket)
    dst = s3.Bucket(dst_bucket)

    if dryrun:
        print('\nDryrun is on, no action will be made for real.\n')

    try:
        print('Processing...\n')
        batch = []
        for obj in src.objects.all():

            skip = False
            if skip_existing:
                keys = list(dst.objects.filter(Prefix=obj.key))
                if len(keys) > 0 and keys[0].key == obj.key:
                    skip = True

            batch.append('{0:s}{4:s}copy: s3://{2:s}/{1:s} to s3://{3:s}/{1:s}'.format(
                '(dryrun) ' if dryrun else '',
                obj.key,
                src_bucket,
                dst_bucket,
                '(skip) ' if skip else ''
            ))

            if len(batch) == 10:
                print('\n'.join(batch))
                batch = []

            if not dryrun and not skip:
                s3.Object(dst_bucket, obj.key).copy_from(
                    ACL=get_canned_acl(obj),
                    CopySource={'Bucket': src_bucket, 'Key': obj.key},
                    MetadataDirective='COPY'
                )
        if len(batch) > 0:
            print('\n'.join(batch))

    except Exception as e:
        print(e)


def print_policy(src_bucket, user_arn):
    print(
'''{{
    "Version": "2012-10-17",
    "Statement": [
        {{
            "Sid": "AllowCopyFromExternalAccount",
            "Effect": "Allow",
            "Principal": {{
                "AWS": "{0:s}"
            }},
            "Action": [
                "s3:GetObject",
                "s3:GetObjectAcl",
                "s3:GetObjectTagging",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::{1:s}",
                "arn:aws:s3:::{1:s}/*"
            ]

        }}
    ]
}}'''.format(user_arn, src_bucket))
    sys.exit()


if sys.version_info[0] < 3:
    sys.exit("This script requires Python version to be 3.x")

if __name__ == '__main__': main()
