// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React from 'react';
import { API } from 'aws-amplify';
import Table from './Table';

export default class AllData extends React.Component {
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
        let querypath = '/search/?scan=all';

        //Loading 
        this.setState({ isloading: true });

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

        const { instances, isLoading, error } = this.state;

        if (error) {
            return <div className="default"><h1><center><br></br>{error.message}</center></h1></div>;
        }

        if (isLoading) {
            return <div className="default"><h1><center><br></br>Loading All Data in DynamoDB...this may take a while</center></h1></div>;
        }

        console.log(this.state.instances.tags)

        const columns = [
            {
                dataField: 'Id',
                text: 'Id',
                hidden: true,
                csvExport: false
            }, {
                dataField: 'AccountNumber',
                text: 'Account',
                sort: true
            }, {
                dataField: 'Region',
                text: 'Region',
                sort: true
            }, {
                dataField: 'EntryType',
                text: 'EntryType',
                sort: true
            },{
                dataField: 'Tags',
                text: 'Tags',
                sort: true
            },{
                dataField: 'PublicIp',
                text: 'PublicIp',
                sort: true,
                hidden: true
            },{
                dataField: 'PrivateIpAddress',
                text: 'PrivateIpAddress',
                sort: true,
                hidden: true
            },{
                dataField: 'CidrBlock',
                text: 'CidrBlock',
                sort: true,
                hidden: true
            },{
                dataField: 'AvailabilityZone',
                text: 'AvailabilityZone',
                sort: true,
                hidden: true
            },{
                dataField: 'InstanceType',
                text: 'InstanceType',
                sort: true,
                hidden: true
            },{
                dataField: 'InstancePlatform',
                text: 'InstancePlatform',
                sort: true,
                hidden: true
            },{
                dataField: 'Arn',
                text: 'Arn',
                sort: true,
                hidden: true
            },{
                dataField: 'Name',
                text: 'Name',
                sort: true,
                hidden: true
            }, {
                dataField: 'PolicyName',
                text: 'PolicyName',
                sort: true,
                hidden: true
            },{
                dataField: 'FunctionName',
                text: 'FunctionName',
                sort: true,
                hidden: true
            },{
                dataField: 'Runtime',
                text: 'Runtime',
                sort: true,
                hidden: true
            }, {
                dataField: 'RoleName',
                text: 'RoleName',
                sort: true,
                hidden: true
            },{
                dataField: 'Tenancy',
                text: 'Tenancy',
                sort: true,
                hidden: true
            },{
                dataField: 'LastModified',
                text: 'LastModified',
                sort: true,
                hidden: true
            },{
                dataField: 'Version',
                text: 'Version',
                sort: true,
                hidden: true
            },{
                dataField: 'DBInstanceClass',
                text: 'DBInstanceClass',
                sort: true,
                hidden: true
            }, {
                dataField: 'State',
                text: 'State',
                sort: true,
                hidden: true
            },{
                dataField: 'Engine',
                text: 'Engine',
                sort: true,
                hidden: true
            },{
                dataField: 'SubnetId',
                text: 'SubnetId',
                sort: true,
                hidden: true
            }, {
                dataField: 'VpcId',
                text: 'VpcId',
                sort: true,
                hidden: true
            },{
                dataField: 'UserName',
                text: 'UserName',
                sort: true,
                hidden: true
            },{
                dataField: 'DhcpOptionsId',
                text: 'DhcpOptionsId',
                sort: true,
                hidden: true
            }]

        return (
            <div className="default" style={{ padding: "20px", fontSize: "14px" }}>
                <center><h2>All DynamoDB Data</h2></center>
                <br />
                <Table data={instances}
                    columns={columns}
                    loading={isLoading}
                    id="Id"
                    sort="AccountNumber"
                    search="name" />
            </div>
        )
    }
}