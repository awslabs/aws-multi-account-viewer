// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React from 'react';
import { API } from 'aws-amplify';
import { Form, Button } from 'react-bootstrap';


class Refresh extends React.Component {
    constructor(props) {
        super(props);

        this.handleClick = this.handleClick.bind(this);
        this.handleChange = this.handleChange.bind(this);

        this.state = {
            inputvalue: '',
            isLoading: false
        }
    }

    handleChange(event) {
        this.setState({
            inputvalue: event.target.value
        })
    }

    handleClick() {

        // API Gateway Info
        let apiName = 'MyAPIGatewayAPI';
        let querypath = '/message/?function=' + this.state.inputvalue;

        console.log('Form value: ' + this.state.inputvalue);
        console.log('query: ' + querypath);

        this.setState({ isLoading: true }, () => {
        API.get(apiName, querypath).then(response => {
            this.setState({ isLoading: false });
            console.log('sent to sqs')
            alert('Successful')
        }).catch(error => {
            console.log(error.response)
            alert('You need to select an options: Failed: ' + error)
        });
        });
      }

    render() {

        const { isLoading } = this.state;

        return (
            <div className="form-refresh">
                <br></br>
                <center>
                    <b>Refresh Checks</b>
                    <br></br><br></br>
                    <Form>
                        <Form.Group controlId="checkboxs">
                            <Form.Label>Individual Refresh</Form.Label>
                            <Form.Control as="select" value={this.state.inputvalue} onChange={this.handleChange}>
                                <option>Select...</option>
                                <option value="ec2">EC2</option>
                                <option value="lambda">Lambda</option>
                                <option value="rds">RDS</option>
                                <option value="odcr">ODCR</option>
                                <option value="iam-users">IAM Users</option>
                                <option value="iam-roles">IAM Roles</option>
                                <option value="iam-attached-policys">IAM Attached Policys</option>
                                <option value="vpc">VPC</option>
                                <option value="network-interfaces">Network Interfaces</option>
                                <option value="subnet">Subnets</option>
                                <option value="org">Organizations</option>
                                <option value="s3-buckets">S3 Buckets</option>
                                <option value="ri">EC2 Reservations</option>
                                <option value="lightsail">Lightsail</option>
                            </Form.Control>
                        </Form.Group>

                        <Form.Group controlId="radioboxes">
                            <Form.Check type="radio" label="All Checks" name="formHorizontalRadios" id="formHorizontalRadios1"
                                onChange={this.handleChange}
                                value="cron"
                                checked={this.state.inputvalue === 'cron'} />
                        </Form.Group>

                        <Button variant="info" type="submit" value="Submit"
                            disabled={isLoading}
                            onClick={!isLoading ? this.handleClick : null}
                        >
                            {isLoading ? 'Loading…' : 'Send To SQS'}
                        </Button>
                    </Form>
                </center>
                <br></br>
                <i>Note: Button will send job to sqs to update, depending on the amount of accounts/regions it may take a while, 
                    gradually increase to see the load</i>
            </div>
        );
    }
}

export default Refresh
