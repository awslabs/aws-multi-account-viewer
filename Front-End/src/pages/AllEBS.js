// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React from 'react';
import { API } from 'aws-amplify';
import Table from './Table';

export default class AllLB extends React.Component {
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
        let querypath = '/search/?scan=ebs';

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
            return <div className="default"><h1><center><br></br>Loading ...</center></h1></div>;
        }

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
                dataField: 'VolumeId',
                text: 'VolumeId',
                sort: true
            }, {
                dataField: 'State',
                text: 'State',
                sort: true
            }, {
                dataField: 'Size',
                text: 'Size',
                sort: true
            }, {
                dataField: 'VolumeType',
                text: 'VolumeType',
                sort: true
            }, {
                dataField: 'Encrypted',
                text: 'Encrypted',
                sort: true
            }, {
                dataField: 'SnapshotId',
                text: 'SnapshotId',
                sort: true
            }, {
                dataField: 'Tags',
                text: 'Tags',
                sort: true
            }]

        return (
            <div className="default" style={{ padding: "20px", fontSize: "14px" }}>
                <center><h2>EBS Volumes</h2></center>
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