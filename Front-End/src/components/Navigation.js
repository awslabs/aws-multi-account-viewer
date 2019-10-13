// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React, { Component } from "react";
import { Navbar, Nav, Button, NavDropdown } from 'react-bootstrap';
import { Auth } from 'aws-amplify';
import NavLink from "react-bootstrap/NavLink";


export class Navigation extends Component {
  constructor(props) {
    super(props);

    this.toggle = this.toggle.bind(this);
    this.state = {
      isOpen: false
    };
  }
  toggle() {
    this.setState({
      isOpen: !this.state.isOpen
    });
  };

  signOut = (e) => {
    Auth.signOut()
  };


    render() {
      return (
        <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
          <Navbar.Brand href="/">Multi Account Viewer</Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="mr-auto">
            <NavDropdown title="EC2" id="collasible-nav-dropdown">
                <NavDropdown.Item href="/allec2">View All EC2 Instances</NavDropdown.Item>
                <NavDropdown.Item href="/allris">View All RIs</NavDropdown.Item>
                <NavDropdown.Item href="/allodcr">View All ODCRs</NavDropdown.Item>
                <NavDropdown.Item href="/alllightsail">View All Lightsail Instances</NavDropdown.Item>
              </NavDropdown>

            <NavDropdown title="Lambda" id="collasible-nav-dropdown">
              <NavDropdown.Item href="/alllambda">All Lambda's</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="IAM" id="collasible-nav-dropdown">
                <NavDropdown.Item href="/AllUsers">All Users</NavDropdown.Item>
                <NavDropdown.Item href="/AllRoles">All Roles</NavDropdown.Item>
                <NavDropdown.Item href="/AllAttachedPolicys">All Attached Policys</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="RDS" id="collasible-nav-dropdown">
                <NavDropdown.Item href="/allrds">All RDS Instances</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="VPC" id="collasible-nav-dropdown">
                <NavDropdown.Item href="/Allvpcs">All VPCs</NavDropdown.Item>
                <NavDropdown.Item href="/Allsubnets">All Subnets</NavDropdown.Item>
                <NavDropdown.Item href="/AllNetworkInterfaces">All All Network Interfaces</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="Organizations" id="collasible-nav-dropdown">
                <NavDropdown.Item href="/organizations">All Active Accounts</NavDropdown.Item>
              </NavDropdown>

              <NavDropdown title="S3" id="collasible-nav-dropdown">
                <NavDropdown.Item href="/AllS3">All S3 Buckets</NavDropdown.Item>
              </NavDropdown>

              <NavLink href="/AllData">All Data</NavLink>
              <NavLink href="/refresh">Refresh Checks</NavLink>
              
            </Nav>

            <Nav>
             <Button type="submit" variant="outline-info" onClick={(e) => { this.signOut(e) }}>Sign Out</Button>
            </Nav>

          </Navbar.Collapse>
        </Navbar>
    );
  }
}
