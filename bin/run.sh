# !/usr/bin/env bash
source ../config/aws_exercise_001.config

aws_profile=$1

if [ -z $aws_profile ]; then
    echo "AWS profile not specified by the user. Using $default_aws_profile by default."
    aws_profile=$default_aws_profile
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

echo "
aws --profile $default_aws_profile \\
    cloudformation package \\
    --template-file $in_template_file \\
    --s3-bucket $reference_s3_bucket \\
    --s3-prefix $reference_s3_bucket_prefix \\
    --output-template-file $out_template_file
"

aws --profile $default_aws_profile \
    cloudformation package \
    --template-file $in_template_file \
    --s3-bucket $reference_s3_bucket \
    --s3-prefix $reference_s3_bucket_prefix \
    --output-template-file $out_template_file

echo "
aws --profile $default_aws_profile \\
    cloudformation deploy \\
    --template-file $out_template_file \\
    --stack-name $stack_name \\
    --capabilities CAPABILITY_IAM \\
    --tags \\
    Name=aws-exercise-001 \\
    Owner=$default_owner \\
    Environment=$default_tag_environment \\
    Classification=$default_classification \\
    Status=$default_status \\
    --no-fail-on-empty-changeset
"
aws --profile $default_aws_profile \
    cloudformation deploy \
    --template-file $out_template_file \
    --stack-name $stack_name \
    --capabilities CAPABILITY_IAM \
    --tags \
    Name=aws-exercise-001 \
    Owner=$default_owner \
    Environment=$default_tag_environment \
    Classification=$default_classification \
    Status=$default_status \
    --no-fail-on-empty-changeset
