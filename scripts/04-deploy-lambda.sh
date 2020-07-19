#!/bin/bash
# Set to fail script if any command fails.
set -e

# TODO - fill in the TODOs
REPO_HOME=TODO-1/aws-multi-account-viewer
LAMBDA_BUCKET=TODO

pushd ${REPO_HOME}/Back-end/lambdas/
zip function.zip *.py

aws s3 cp function.zip s3://${LAMBDA_BUCKET}

rm function.zip

popd
