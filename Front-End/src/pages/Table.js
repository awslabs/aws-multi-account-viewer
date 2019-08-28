import React, {Component} from 'react';
import ToolkitProvider, {Search} from 'react-bootstrap-table2-toolkit';
import BootstrapTable from 'react-bootstrap-table-next';
import paginationFactory from 'react-bootstrap-table2-paginator';
import overlayFactory from 'react-bootstrap-table2-overlay';
import filterFactory from 'react-bootstrap-table2-filter';
import { Button } from 'react-bootstrap';

//Const search bar using 'react-bootstrap-table2-toolkit' component
const {SearchBar} = Search;

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
            Showing { from } to { to } of { size } Results
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
                    <center><Button type="button" variant="outline-info" size="sm" onClick={ handleClick }> Refresh Page</Button></center>
                </div>
            );
        };

        // const selectRow = {
        //     mode: 'radio', // single row selection
        //     clickToSelect: true
        //   };

        // const rowEvents = {
        //     onClick: (e, row, rowIndex) => {
        //     console.log(JSON.stringify(row))
        //     }
        //   };

        //Return a custom table with a search bar
        return (
            <ToolkitProvider
                keyField={this.props.id}
                data={this.props.data}
                columns={this.props.columns}
                search
            >{props => (
                <div>
                    <RefreshPage { ...props.RefreshPage } />
                    <MyExportCSV { ...props.csvProps } />
                    <br /><SearchBar  {...props.searchProps}
                                     className="custom-search-field"
                                     placeholder={`Search ${this.props.search}`}/><br/>
                    <BootstrapTable defaultSorted={defaultSorted} {...props.baseProps} 
                                    pagination={paginationFactory(options)}
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