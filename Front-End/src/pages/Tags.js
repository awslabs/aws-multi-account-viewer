// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React from 'react';
import { API } from 'aws-amplify';
import { Form, Button } from 'react-bootstrap';


class Tags extends React.Component {
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
                alert('Failed: ' + JSON.stringify(error.response.data))
            });
        });
    }

    render() {

        const { isLoading } = this.state;

        return (
            <div className="form-refresh">
                <br></br>
                <center>
                    <b>Search Tags</b>
                    <br></br>
                    <Form>
                        <Form.Group controlId="searchTags">
                            <Form.Control as="textarea" placeholder="Enter a word contained in tags...."
                                value={this.state.inputvalue} onChange={this.handleChange}>
                            </Form.Control>
                        </Form.Group>
                        {/* <Button type="submit" variant="outline-info" handleChange={(e) => { this.handleClick() }}>Sign Out</Button> */}
                        <Button variant="info" type="submit" value="Submit"
                            disabled={isLoading}
                            onClick={!isLoading ? this.handleClick : null}
                        >
                            {isLoading ? 'Loading…' : 'Send To SQS'}
                        </Button>
                    </Form>
                </center >
                <br></br>
                <i>Note: searching....</i>
            </div >
        );
    }
}

export default Tags;
