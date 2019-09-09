// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React from 'react';
import { API } from 'aws-amplify';
import Table from './Table';

export default class AllLambda extends React.Component {
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
        let querypath = '/search/?scan=lambda';

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
                text: 'AccountNumber',
                sort: true
            }, {
                dataField: 'Region',
                text: 'Region',
                sort: true
            },{
                dataField: 'FunctionName',
                text: 'FunctionName',
                sort: true
            }, {
                dataField: 'Runtime',
                text: 'Runtime',
                sort: true
            }, {
                dataField: 'Timeout',
                text: 'Timeout',
                sort: true
            }, {
                dataField: 'MemorySize',
                text: 'MemorySize',
                sort: true
            }, {
                dataField: 'RoleName',
                text: 'RoleName',
                sort: true
            }, {
                dataField: 'LastModified',
                text: 'LastModified',
                sort: true
            }]
        return (
                <div className="default" style={{ padding: "20px", fontSize: "14px" }}>
                    <center><h2>All Lambda</h2></center>
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