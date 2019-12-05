# !/usr/bin/env bash

file_name=$1
bucket_name=$2
prefix=$3
aws_profile=$4

if [ $# -lt 3 ]; then
    echo "Usage: upload.sh file_name bucket_name bucket_prefix [aws profile]"
    exit -1
fi

if [ -z $aws_profile ]; then
    echo "AWS profile not specified by the user. Using jumo-dev by default."
    aws_profile="jumo-dev"
fi

region="$(aws --profile $aws_profile configure get region)"
account_id="$(aws --profile $aws_profile sts get-caller-identity --output text --query 'Account')"

echo "\n============================="
echo "AWS Profile: $aws_profile"
echo "Region: $region"
echo "Account ID: $account_id"
echo "=============================\n"

if [ -z $region ] || [ -z $account_id ]; then
    echo "Unable to fetch region or account id."
    exit 1
fi

aws --profile $aws_profile s3 cp $file_name s3://${bucket_name}/${prefix}/
