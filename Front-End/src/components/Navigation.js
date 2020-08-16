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
            <NavDropdown title="Compute" id="collasible-nav-dropdown">
              <NavDropdown.Item href="/allec2">EC2 Instances</NavDropdown.Item>
              <NavDropdown.Item href="/allLB">Load Balancers</NavDropdown.Item>
              <NavDropdown.Item href="/alllambda">Lambda's</NavDropdown.Item>
              <NavDropdown.Item href="/allris">Reserved Instances</NavDropdown.Item>
              <NavDropdown.Item href="/allodcr">ODCRs</NavDropdown.Item>
              <NavDropdown.Item href="/alleks">EKS</NavDropdown.Item>
              <NavDropdown.Item href="/alllightsail">Lightsail Instances</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Storage" id="collasible-nav-dropdown">
              <NavDropdown.Item href="/AllS3">S3 Buckets</NavDropdown.Item>
              <NavDropdown.Item href="/AllEBS">EBS Volumes</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="Security" id="collasible-nav-dropdown">
              <NavDropdown.Item href="/organizations">Accounts</NavDropdown.Item>
              <NavDropdown.Item href="/AllUsers">Users</NavDropdown.Item>
              <NavDropdown.Item href="/AllRoles">Roles</NavDropdown.Item>
              <NavDropdown.Item href="/AllAttachedPolicys">Attached Policys</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="RDS" id="collasible-nav-dropdown">
              <NavDropdown.Item href="/allrds">RDS</NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title="VPC" id="collasible-nav-dropdown">
              <NavDropdown.Item href="/Allvpcs">VPCs</NavDropdown.Item>
              <NavDropdown.Item href="/Allsubnets">Subnets</NavDropdown.Item>
              <NavDropdown.Item href="/AllNetworkInterfaces">Network Interfaces</NavDropdown.Item>
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
