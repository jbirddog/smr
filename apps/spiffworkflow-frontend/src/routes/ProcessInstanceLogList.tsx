import { useEffect, useState } from 'react';
import { Table } from 'react-bootstrap';
import { useParams, useSearchParams } from 'react-router-dom';
import PaginationForTable from '../components/PaginationForTable';
import ProcessBreadcrumb from '../components/ProcessBreadcrumb';
import {
  getPageInfoFromSearchParams,
  convertSecondsToFormattedDate,
} from '../helpers';
import HttpService from '../services/HttpService';

export default function ProcessInstanceLogList() {
  const params = useParams();
  const [searchParams] = useSearchParams();
  const [processInstanceLogs, setProcessInstanceLogs] = useState([]);
  const [pagination, setPagination] = useState(null);

  useEffect(() => {
    const setProcessInstanceLogListFromResult = (result: any) => {
      setProcessInstanceLogs(result.results);
      setPagination(result.pagination);
    };
    const { page, perPage } = getPageInfoFromSearchParams(searchParams);
    HttpService.makeCallToBackend({
      path: `/process-models/${params.process_group_id}/${params.process_model_id}/process-instances/${params.process_instance_id}/logs?per_page=${perPage}&page=${page}`,
      successCallback: setProcessInstanceLogListFromResult,
    });
  }, [searchParams, params]);

  const buildTable = () => {
    // return null;
    const rows = processInstanceLogs.map((row) => {
      const rowToUse = row as any;
      return (
        <tr key={rowToUse.id}>
          <td>{rowToUse.bpmn_process_identifier}</td>
          <td>{rowToUse.message}</td>
          <td>{rowToUse.bpmn_task_identifier}</td>
          <td>{rowToUse.bpmn_task_name}</td>
          <td>{rowToUse.bpmn_task_type}</td>
          <td>{rowToUse.username}</td>
          <td>{convertSecondsToFormattedDate(rowToUse.timestamp)}</td>
        </tr>
      );
    });
    return (
      <Table striped bordered>
        <thead>
          <tr>
            <th>Bpmn Process Identifier</th>
            <th>Message</th>
            <th>Task Identifier</th>
            <th>Task Name</th>
            <th>Task Type</th>
            <th>User</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </Table>
    );
  };

  if (pagination) {
    const { page, perPage } = getPageInfoFromSearchParams(searchParams);
    return (
      <main>
        <ProcessBreadcrumb
          processModelId={params.process_model_id}
          processGroupId={params.process_group_id}
          linkProcessModel
        />
        <PaginationForTable
          page={page}
          perPage={perPage}
          pagination={pagination}
          tableToDisplay={buildTable()}
          path={`/admin/process-models/${params.process_group_id}/${params.process_model_id}/process-instances/${params.process_instance_id}/logs`}
        />
      </main>
    );
  }
  return null;
}
