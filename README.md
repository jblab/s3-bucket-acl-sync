# S3 Bucket ACL Sync

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](LICENSE)
[![Latest Release](https://img.shields.io/github/release/jblab/s3-bucket-acl-sync.svg?style=flat-square)](https://github.com/jblab/s3-bucket-acl-sync/releases/latest)

This is a simple Python script that allows to copy files from one S3 Bucket to
another preserving the Public ACL.

## Requirements

- Python 3
- [AWS Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## Usage

```shell
s3sync.py [-h] [-K KEY] [-S SECRET] [-s BUCKET] [-d BUCKET] [-P PROFILE] [--dryrun] [--list] [--get-policy] [--skip-existing]
```

### Options

| Option                        | Description                                                                                                |
|-------------------------------|------------------------------------------------------------------------------------------------------------|
| -h, --help                    | Show help message and exit                                                                                 |
| -K KEY, --key KEY             | AWS access key id, this has precedence over --profile option.                                              |
| -S SECRET, --secret SECRET    | AWS secret acces key.                                                                                      |
| -s BUCKET, --src BUCKET       | Source S3 bucket name.                                                                                     |
| -d BUCKET, --dst BUCKET       | Destination S3 bucket name.                                                                                |
| -P PROFILE, --profile PROFILE | AWS profile to use.                                                                                        |
| --dryrun                      | Displays the operations that would be performed using the specified command without actually running them. |
| --list                        | Only lists files in source and/or destination bucket(s).                                                   |
| --get-policy                  | Prints out the policy required in the source bucket to allow the copy across AWS accounts.                 |
| --skip-existing               | Skips existing key names, does not check that files are the same.                                          | 

## Changelog

Please consult the [CHANGELOG](CHANGELOG.md) for more information about the version history.

## License

This project is licensed under the Apache 2.0 license. See the [LICENSE](LICENSE) for details.

## Contributing

Please read [CONTRIBUTING](CONTRIBUTING.md) for details on the process for contributing to this project.

Be mindful of our [Code of Conduct](CODE_OF_CONDUCT.md).
