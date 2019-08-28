import React from 'react';
import { API } from 'aws-amplify';
import Table from './Table';

export default class AllRis extends React.Component {
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
        let querypath = '/search/?scan=ri';

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
                dataField: 'InstanceCount',
                text: 'InstanceCount',
                sort: true
            }, {
                dataField: 'InstanceType',
                text: 'InstanceType',
                sort: true
            }, {
                dataField: 'Scope',
                text: 'Scope',
                sort: true
            }, {
                dataField: 'ProductDescription',
                text: 'ProductDescription',
                sort: true
            }, {
                dataField: 'ReservedInstancesId',
                text: 'ReservedInstancesId',
                sort: true
            }, {
                dataField: 'Start',
                text: 'Start',
                sort: true
            }, {
                dataField: 'End',
                text: 'End',
                sort: true
            },{
                dataField: 'InstanceTenancy',
                text: 'InstanceTenancy',
                sort: true
            },{
                dataField: 'OfferingClass',
                text: 'OfferingClass',
                sort: true
            }]
        return (
                <div className="default" style={{ padding: "20px", fontSize: "14px" }}>
                    <center><h2>All EC2 Reservations</h2></center>
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


