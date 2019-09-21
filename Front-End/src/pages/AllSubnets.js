// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React from 'react';
import { API } from 'aws-amplify';
import Table from './Table';

export default class AllSubnets extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            instances: [],
            isLoading: true
        };
    }

    componentDidMount() {

        // API Gateway
        let apiName = 'MyAPIGatewayAPI';
        let querypath = '/search/?scan=subnet';

        // Loading 
        this.setState({ isLoading: true });

        // Scan DynamoDB for results
        API.get(apiName, querypath).then(response => {
            this.setState({
                instances: response,
                isLoading: false
            });
        })
            .then(response => {
                console.log(this.state.instances)
            })
            .catch(error => {
                this.setState({ error, isLoading: false })
                console.log(error.response)
            });
    }
    render() {

        const { isLoading, error, instances } = this.state;

        if (error) {
            return <div className="default"><h1><center><br></br>{error.message}</center></h1></div>;
        }

        if (isLoading) {
            return <div className="default"><h1><center><br></br>Loading ...</center></h1></div>;
        }

        const columns = [
            {
                dataField: 'Id',
                text: 'Id',
                hidden: true,
            }, {
                dataField: 'AccountNumber',
                text: 'Account',
                sort: true
            }, {
                dataField: 'Region',
                text: 'Region',
                sort: true
            },{
                dataField: 'CidrBlock',
                text: 'CidrBlock',
                sort: true
            }, {
                dataField: 'AvailabilityZone',
                text: 'AvailabilityZone',
                sort: true
            }, {
                dataField: 'AvailabilityZoneId',
                text: 'AvailabilityZoneId',
                sort: true
            }, {
                dataField: 'SubnetId',
                text: 'SubnetId',
                sort: true
            }, {
                dataField: 'VpcId',
                text: 'VpcId',
                sort: true
            }, {
                dataField: 'AvailableIpAddressCount',
                text: 'AvailableIpAddressCount',
                sort: true
            }]
        return (
                <div className="default" style={{ padding: "20px", fontSize: "14px" }}>
                    <center><h2>All Subnets</h2></center>
                    <br />
                    <Table data={instances}
                           columns={columns}
                           id="Id"
                           sort="AccountNumber"
                           search="name"/>
                </div>
                )
    }
}

