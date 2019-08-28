import React, { Component } from 'react';
import { BrowserRouter, Route } from "react-router-dom";
import Amplify, { Auth } from 'aws-amplify';
import { withAuthenticator, SignIn, ConfirmSignIn, Greetings, VerifyContact, RequireNewPassword, ForgotPassword, Loading } from 'aws-amplify-react';
import MyTheme from "./components/AmplifyTheme";
import { Home } from './pages/Home';
import { Navigation } from './components/Navigation';
import AllEC2 from './pages/AllEC2';
import AllRDS from './pages/AllRDS';
import AllODCR from './pages/AllODCR';
import AllRis from './pages/AllRis';
import Organizations from './pages/Organizations';
import AllVpcs from './pages/AllVpcs';
import AllSubnets from './pages/AllSubnets';
import Refresh from './pages/Refresh';
import AllUsers from './pages/AllUsers';
import AllRoles from './pages/AllRoles';
import AllAttachedPolicys from './pages/AllAttachedPolicys';
import AllLambda from './pages/AllLambda';
import Table from './pages/Table';
import './index.css';


Amplify.configure({
  // OPTIONAL - if your API requires authentication 
  Auth: {
    // REQUIRED - Amazon Cognito Region
    region: 'ap-southeast-2',
    // OPTIONAL - Amazon Cognito User Pool ID
    userPoolId: 'ap-southeast-2_pfhwrGsU1',
    // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
    userPoolWebClientId: '3q7fo0rivd5oinl70u27bnhidq'
  },
  API: {
    endpoints: [
      {
        name: "MyAPIGatewayAPI",
        endpoint: "https://q6h3hc46ya.execute-api.ap-southeast-2.amazonaws.com/prod",
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
          <Route path="/alllambda" component={AllLambda} />
          <Route path="/Table" component={Table} />
          <Route path="/allodcr" component={AllODCR} />
          <Route path="/organizations" component={Organizations} />
          <Route path="/allrds" component={AllRDS} />
          <Route path="/allvpcs" component={AllVpcs} />
          <Route path="/allsubnets" component={AllSubnets} />
          <Route path="/refresh" component={Refresh} />
          <Route path="/allusers" component={AllUsers} />
          <Route path="/allroles" component={AllRoles} />
          <Route path="/allattachedpolicys" component={AllAttachedPolicys} />
          <Route path="/allris" component={AllRis} />
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
