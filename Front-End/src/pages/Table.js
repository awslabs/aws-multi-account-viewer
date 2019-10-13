// Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

import React, { Component } from 'react';
import { Row, Col } from 'reactstrap';
import ToolkitProvider, { Search, ColumnToggle } from 'react-bootstrap-table2-toolkit';
import BootstrapTable from 'react-bootstrap-table-next';
import paginationFactory from 'react-bootstrap-table2-paginator';
import overlayFactory from 'react-bootstrap-table2-overlay';
import filterFactory from 'react-bootstrap-table2-filter';
import { Button } from 'react-bootstrap';

//Const search bar using 'react-bootstrap-table2-toolkit' component
const { SearchBar } = Search;
const { ToggleList } = ColumnToggle;

//Component class that renders a fully customized and responsive table using 'react-bootstrap-table2'
export class Table extends Component {

    render() {

        //Define the default sorting options (col & asc)
        const defaultSorted = [{
            dataField: this.props.sort,
            order: 'asc'
        }];

        //Define pagination options
        const customTotal = (from, to, size) => (
            <span className="react-bootstrap-table-pagination-total">
                Showing {from} to {to} of {size} Results
            </span>
        );

        //Define the options of the table (nb of rows/pagination, etc)
        const options = {
            paginationSize: 100,
            pageStartIndex: 1,
            hideSizePerPage: false,
            hidePageListOnlyOnePage: true,
            firstPageText: 'First',
            prePageText: 'Back',
            nextPageText: 'Next',
            lastPageText: 'Last',
            nextPageTitle: 'First page',
            prePageTitle: 'Pre page',
            firstPageTitle: 'Next page',
            lastPageTitle: 'Last page',
            showTotal: true,
            paginationTotalRenderer: customTotal,
            sizePerPageList: [{
                text: '100', value: 100
            }]
        };

        // Export CSV
        const MyExportCSV = (props) => {
            const handleClick = () => {
                props.onExport();
            };
            return (
                <div>
                    <Button type="button" variant="outline-info" size="sm" onClick={handleClick}>Export to CSV</Button>
                </div>
            );
        };

        // Refesh button
        const RefreshPage = () => {
            const handleClick = () => {
                window.location.reload()
            };
            return (
                <div>
                    <center><Button type="button" variant="outline-info" size="sm" onClick={handleClick}> Refresh Page</Button></center>
                </div>
            );
        };

        const expandRow = {
            renderer: row => (
              <div>
                  <pre>
                { `${JSON.stringify(row, undefined, 2)}`}
                </pre>
              </div>
            ),
            showExpandColumn: true,
            expandHeaderColumnRenderer: ({ isAnyExpands }) => {
              if (isAnyExpands) {
                return <b>-</b>;
              }
              return <b>+</b>;
            },
            expandColumnRenderer: ({ expanded }) => {
              if (expanded) {
                return (
                  <b>-</b>
                );
              }
              return (
                <b>...</b>
              );
            }
          };

        //Return a custom table with a search bar
        return (
            <ToolkitProvider
                keyField={this.props.id}
                data={this.props.data}
                columns={this.props.columns}
                columnToggle
                search
            >{props => (
                <div>
                    <Row><Col xs="6">
                        <b>Toggle Columns:  </b>
                    <ToggleList 
                        contextual="outline-info"
                        className="list-custom-class"
                        btnClassName="btn-sm"
                                { ...props.columnToggleProps }/></Col></Row>      
                    <br></br>
                    <Row><Col xs="sm">
                    <SearchBar  {...props.searchProps}
                                     className="search-label"
                                     type="text"
                                     placeholder={`Search any ${this.props.search} across columns`}/></Col>
                                     <Col xs="auto">
                                     <RefreshPage { ...props.RefreshPage } /> </Col>
                                     <Col xs="auto">
                                     <MyExportCSV { ...props.csvProps } /></Col></Row>
                    <BootstrapTable defaultSorted={defaultSorted} {...props.baseProps} 
                                    pagination={paginationFactory(options)}
                                    expandRow={ expandRow }
                                    // rowEvents={ rowEvents }
                                    // selectRow={selectRow}
                                    condensed={ true }
                                    filter={ filterFactory()}
                                    noDataIndication={'No Results Found'}
                                    overlay={ overlayFactory() }
                                    striped
                                    hover 
                                    />
                </div>
            )}
            </ToolkitProvider>)
    }
}
export default Table;