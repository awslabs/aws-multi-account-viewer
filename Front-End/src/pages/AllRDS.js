// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React from 'react';
import { API } from 'aws-amplify';
import Table from './Table';

export default class AllRDS extends React.Component {
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
        let querypath = '/search/?scan=rds';

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
                dataField: 'Id',
                text: 'DBInstanceIdentifier',
                sort: true
            }, {
                dataField: 'DBInstanceClass',
                text: 'DBInstanceClass',
                sort: true
            }, {
                dataField: 'State',
                text: 'State',
                sort: true
            },{
                dataField: 'Engine',
                text: 'Engine',
                sort: true
            }, {
                dataField: 'MultiAZ',
                text: 'MultiAZ',
                sort: true
            }, {
                dataField: 'PubliclyAccessible',
                text: 'PubliclyAccessible',
                sort: true
            },{
                dataField: 'Tags',
                text: 'Tags',
                sort: true,
                hidden: true
            },{
                dataField: 'AllocatedStorage',
                text: 'AllocatedStorage',
                sort: true,
                hidden: true
            },{
                dataField: 'PreferredBackupWindow',
                text: 'PreferredBackupWindow',
                sort: true,
                hidden: true
            },{
                dataField: 'BackupRetentionPeriod',
                text: 'BackupRetentionPeriod',
                sort: true,
                hidden: true
            },{
                dataField: 'PreferredMaintenanceWindow',
                text: 'PreferredMaintenanceWindow',
                sort: true,
                hidden: true
            },{
                dataField: 'StorageType',
                text: 'StorageType',
                sort: true,
                hidden: true
            }]
        return (
                <div className="default" style={{ padding: "20px", fontSize: "14px" }}>
                    <center><h2>All RDS Instances</h2></center>
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