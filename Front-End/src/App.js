// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React, { Component } from 'react';
import { BrowserRouter, Route } from "react-router-dom";
import Amplify, { Auth } from 'aws-amplify';
import { withAuthenticator, SignIn, ConfirmSignIn, Greetings, VerifyContact, RequireNewPassword, ForgotPassword, Loading } from 'aws-amplify-react';
import MyTheme from "./components/AmplifyTheme";
import { Home } from './pages/Home';
import { Navigation } from './components/Navigation';
import AllEC2 from './pages/AllEC2';
import AllEKS from './pages/AllEKS';
import AllRDS from './pages/AllRDS';
import AllODCR from './pages/AllODCR';
import AllRis from './pages/AllRis';
import Organizations from './pages/Organizations';
import AllVpcs from './pages/AllVpcs';
import AllNetworkInterfaces from './pages/AllNetworkInterfaces';
import AllSubnets from './pages/AllSubnets';
import Refresh from './pages/Refresh';
import AllData from './pages/AllData';
import AllUsers from './pages/AllUsers';
import AllRoles from './pages/AllRoles';
import AllAttachedPolicys from './pages/AllAttachedPolicys';
import AllLambda from './pages/AllLambda';
import AllS3 from './pages/AllS3';
import AllLightsail from './pages/AllLightsail';
import Table from './pages/Table';
import './index.css';


Amplify.configure({
  // OPTIONAL - if your API requires authentication 
  Auth: {
    // REQUIRED - Amazon Cognito Region
    region: 'ap-southeast-2',
    // OPTIONAL - Amazon Cognito User Pool ID
    userPoolId: process.env.REACT_APP_USERPOOL_ID,
    // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
    userPoolWebClientId: process.env.REACT_APP_USERPOOL_WEB_CLIENT_ID,
  },
  API: {
    endpoints: [
      {
        name: "MyAPIGatewayAPI",
        endpoint: process.env.REACT_APP_PIG_ENDPOINT,
        region: 'ap-southeast-2',
        custom_header: async () => {
          return { Authorization: (await Auth.currentSession()).idToken.jwtToken };
        }
      }
    ]
  }
});


class App extends Component {

  render() {
    return (
      <BrowserRouter>
        <div>
          <Navigation />
          <Route exact path="/" component={Home} />
          <Route path="/allec2" component={AllEC2} />
          <Route path="/alleks" component={AllEKS} />
          <Route path="/alllambda" component={AllLambda} />
          <Route path="/Table" component={Table} />
          <Route path="/allodcr" component={AllODCR} />
          <Route path="/organizations" component={Organizations} />
          <Route path="/allrds" component={AllRDS} />
          <Route path="/allvpcs" component={AllVpcs} />
          <Route path="/allnetworkinterfaces" component={AllNetworkInterfaces} />
          <Route path="/allsubnets" component={AllSubnets} />
          <Route path="/refresh" component={Refresh} />
          <Route path="/alldata" component={AllData} />
          <Route path="/allusers" component={AllUsers} />
          <Route path="/allroles" component={AllRoles} />
          <Route path="/allattachedpolicys" component={AllAttachedPolicys} />
          <Route path="/allris" component={AllRis} />
          <Route path="/alls3" component={AllS3} />
          <Route path="/alllightsail" component={AllLightsail} />
        </div>
      </BrowserRouter>
    );
  }
}

// * turn off Auth *
// export default App;

// * Turn on Auth *
export default withAuthenticator(App, false, [
  <Greetings />,
  <SignIn />,
  <ConfirmSignIn />,
  <VerifyContact />,
  <ForgotPassword />,
  <RequireNewPassword />,
  <Loading />
], null, MyTheme)
