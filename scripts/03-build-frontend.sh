#!/bin/bash
# Set to fail script if any command fails.
set -e

# TODO - fill in the TODOs
REPO_HOME=TODO-1/aws-multi-account-viewer
USER_POOL_ID=TODO
USER_POOL_WEB_CLIENT_ID=TODO
APIG_ID=TODO
FRONTEND_BUCKET=TODO

cat > ${REPO_HOME}/Front-End/.env << EOF
REACT_APP_APIG_ENDPOINT=https://${APIG_ID}.execute-api.ap-southeast-2.amazonaws.com/v1
REACT_APP_USERPOOL_ID=${USER_POOL_ID}
REACT_APP_USERPOOL_WEB_CLIENT_ID=${USER_POOL_WEB_CLIENT_ID}
EOF

# Install node, yarn
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
nvm install node
node -e "console.log('Running Node.js ' + process.version)"
npm install -g yarn
yarn install

# You may also need
# npm install -g @aws-amplify/cli
# npm install react-scripts --save

pushd ${REPO_HOME}/Front-End/
yarn
yarn build
#yarn start

aws s3 sync build/ s3://${FRONTEND_BUCKET}
popd
