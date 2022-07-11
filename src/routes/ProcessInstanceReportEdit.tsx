import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from 'react-bootstrap';
import { BACKEND_BASE_URL, HOT_AUTH_TOKEN } from '../config';
import ProcessBreadcrumb from '../components/ProcessBreadcrumb';

type ReportColumn = {
  Header: string;
  accessor: string;
};

type ReportFilterBy = {
  field_name: string;
  operator: string;
  field_value: string;
};

export default function ProcessInstanceReportEdit() {
  const params = useParams();
  const navigate = useNavigate();

  const [columns, setColumns] = useState('');
  const [orderBy, setOrderBy] = useState('');
  const [filterBy, setFilterBy] = useState('');

  useEffect(() => {
    function getProcessInstanceReport() {
      fetch(
        `${BACKEND_BASE_URL}/process-models/${params.process_group_id}/${params.process_model_id}/process-instances/reports/${params.report_identifier}?per_page=1`,
        {
          headers: new Headers({
            Authorization: `Bearer ${HOT_AUTH_TOKEN}`,
          }),
        }
      )
        .then((res) => res.json())
        .then(
          (result) => {
            const reportMetadata = result.report_metadata;
            const columnCsv = reportMetadata.columns
              .map((column: ReportColumn) => column.accessor)
              .join(',');
            setColumns(columnCsv);

            if (reportMetadata.order_by) {
              setOrderBy(reportMetadata.order_by.join(','));
            }
            const filterByCsv = reportMetadata.filter_by
              .map(
                (filterByItem: ReportFilterBy) =>
                  `${filterByItem.field_name}=${filterByItem.field_value}`
              )
              .join(',');
            setFilterBy(filterByCsv);
          },
          (error) => {
            console.log(error);
          }
        );
    }

    getProcessInstanceReport();
  }, [params]);

  const editProcessInstanceReport = (event: any) => {
    event.preventDefault();

    const columnArray = columns.split(',').map((column) => {
      return { Header: column, accessor: column };
    });
    const orderByArray = orderBy.split(',').filter((n) => n);

    const filterByArray = filterBy
      .split(',')
      .map((filterByItem) => {
        const [fieldName, fieldValue] = filterByItem.split('=');
        if (fieldValue) {
          return {
            field_name: fieldName,
            operator: 'equals',
            field_value: fieldValue,
          };
        }
        return null;
      })
      .filter((n) => n);

    fetch(
      `${BACKEND_BASE_URL}/process-models/${params.process_group_id}/${params.process_model_id}/process-instances/reports/${params.report_identifier}`,
      {
        headers: new Headers({
          'Content-Type': 'application/json',
          Authorization: `Bearer ${HOT_AUTH_TOKEN}`,
        }),
        method: 'PUT',
        body: JSON.stringify({
          report_metadata: {
            columns: columnArray,
            order_by: orderByArray,
            filter_by: filterByArray,
          },
        }),
      }
    ).then(
      () => {
        navigate(
          `/admin/process-models/${params.process_group_id}/${params.process_model_id}/process-instances/reports/${params.report_identifier}`
        );
      },
      // Note: it's important to handle errors here
      // instead of a catch() block so that we don't swallow
      // exceptions from actual bugs in components.
      (newError) => {
        console.log(newError);
      }
    );
  };

  const deleteProcessInstanceReport = () => {
    fetch(
      `${BACKEND_BASE_URL}/process-models/${params.process_group_id}/${params.process_model_id}/process-instances/reports/${params.report_identifier}`,
      {
        headers: new Headers({
          Authorization: `Bearer ${HOT_AUTH_TOKEN}`,
        }),
        method: 'DELETE',
      }
    ).then(
      () => {
        navigate(
          `/admin/process-models/${params.process_group_id}/${params.process_model_id}/process-instances/reports`
        );
      },
      (error) => {
        console.log(error);
      }
    );
  };

  return (
    <main style={{ padding: '1rem 0' }}>
      <ProcessBreadcrumb />
      <h2>Edit Process Instance Report: {params.report_identifier}</h2>
      <Button onClick={deleteProcessInstanceReport} variant="danger">
        Delete report
      </Button>
      <br />
      <br />
      <form onSubmit={editProcessInstanceReport}>
        <label htmlFor="columns">
          columns:
          <input
            name="columns"
            id="columns"
            type="text"
            value={columns}
            onChange={(e) => setColumns(e.target.value)}
          />
        </label>
        <br />
        <label htmlFor="order_by">
          order_by:
          <input
            name="order_by"
            id="order_by"
            type="text"
            value={orderBy}
            onChange={(e) => setOrderBy(e.target.value)}
          />
        </label>
        <br />
        <br />
        <p>Like: month=3,milestone=2</p>
        <label htmlFor="filter_by">
          filter_by:
          <input
            name="filter_by"
            id="filter_by"
            type="text"
            value={filterBy}
            onChange={(e) => setFilterBy(e.target.value)}
          />
        </label>
        <br />
        <button type="submit">Submit</button>
      </form>
    </main>
  );
}
