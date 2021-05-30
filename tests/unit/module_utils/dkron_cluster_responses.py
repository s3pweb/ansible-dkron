import json


class MockedReponse(object):

    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


def cluster_query_status_response_success():

    server_response = json.dumps({'agent': {
            'name':'ip-172-16-1-63',
            'version':'3.1.3'
        },
        'serf': {
            'coordinate_resets':'0',
            'encrypted':'false',
            'event_queue':'0',
            'event_time':'1',
            'failed':'0',
            'health_score':'0',
            'intent_queue':'0',
            'left':'0',
            'member_time':'2',
            'members':'2',
            'query_queue':'0',
            'query_time':'1'
        },'tags': {
            'dc':'dc1',
            'expect':'2',
            'port':'6868',
            'region':'global',
            'role':'dkron',
            'rpc_addr':'172.16.1.63:6868',
            'server':'true',
            'version':'3.1.3'
        }
    })
    return (MockedReponse(server_response), {'status': 200})


def cluster_query_leader_response_success():

    server_response = json.dumps({
        'Name': 'ip-172-16-0-1',
        'Addr': '172.16.0.1',
        'Port': 8946,
        'Tags': {
            'dc': 'dc1',
            'expect': '2',
            'port': '6868',
            'region': 'global',
            'role': 'dkron',
            'rpc_addr': '172.16.0.1:6868',
            'server': 'true',
            'version': '3.1.3'
        },
        'Status': 1,
        'ProtocolMin': 1,
        'ProtocolMax': 5,
        'ProtocolCur': 2,
        'DelegateMin': 2,
        'DelegateMax': 5,
        'DelegateCur': 4
    })
    return (MockedReponse(server_response), {'status': 200})


def cluster_query_members_response_success():

    server_response = json.dumps([
        {
            'Name':'ip-172-16-0-1',
            'Addr':'172.16.0.1',
            'Port':8946,
            'Tags': {
                'dc':'dc1',
                'expect':'2',
                'port':'6868',
                'region':'global',
                'role':'dkron',
                'rpc_addr':'172.16.0.1:6868',
                'server':'true',
                'version':'3.1.3'
            },
            'Status':1,
            'ProtocolMin':1,
            'ProtocolMax':5,
            'ProtocolCur':2,
            'DelegateMin':2,
            'DelegateMax':5,
            'DelegateCur':4,
            'id':'60d3965c-70df-19ab-f98b-3639241a092e'
        },
        {
            'Name':'ip-172-16-0-2',
            'Addr':'172.16.0.2',
            'Port':8946,
            'Tags': {
                'dc':'dc1',
                'expect':'2',
                'port':'6868',
                'region':'global',
                'role':'dkron',
                'rpc_addr':'172.16.0.2:6868',
                'server':'true',
                'version':'3.1.3'
            },
            'Status':1,
            'ProtocolMin':1,
            'ProtocolMax':5,
            'ProtocolCur':2,
            'DelegateMin':2,
            'DelegateMax':5,
            'DelegateCur':4,
            'id':'c40191ac-fe26-b7f4-c85d-e2858d0c834d'
        }
    ])
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_job_list_response_success():

    server_response = json.dumps([
        {
            'id': 'job',
            'name': 'job',
            'displayname': '',
            'timezone': '',
            'schedule': '@every 1m',
            'owner': 'guy',
            'owner_email': 'guy@bluebatgames.com',
            'success_count': 145395,
            'error_count': 0,
            'last_success': '2021-05-27T05: 29: 24.030944666Z',
            'last_error': 'null',
            'disabled': 'false',
            'tags': {
            'server': 'true: 1'},
            'metadata': 'null',
            'retries': 0,
            'dependent_jobs': 'null',
            'parent_job': '',
            'processors': {
            },
            'concurrency': 'allow',
            'executor': 'shell',
            'executor_config': {
            'command': '/bin/true'},
            'status': 'success',
            'next': '2021-05-27T05: 30: 24Z'
        },
        {
            'id': 'job2',
            'name': 'job2',
            'displayname': '',
            'timezone': '',
            'schedule': '@every 10m',
            'owner': 'guy',
            'owner_email': 'guy@bluebatgames.com',
            'success_count': 14498,
            'error_count': 0,
            'last_success': '2021-05-27T05: 25: 24.023101544Z',
            'last_error': 'null',
            'disabled': 'false',
            'tags': {
            'server': 'true: 1'},
            'metadata': 'null',
            'retries': 0,
            'dependent_jobs': 'null',
            'parent_job': '',
            'processors': {
            },
            'concurrency': 'allow',
            'executor': 'shell',
            'executor_config': {
            'command': '/bin/true'},
            'status': 'success',
            'next': '2021-05-27T05: 35: 24Z'
        },
        {
            'id': 'job3',
            'name': 'job3',
            'displayname': '',
            'timezone': '',
            'schedule': '@every 60m',
            'owner': 'guy',
            'owner_email': 'guy@bluebatgames.com',
            'success_count': 2398,
            'error_count': 0,
            'last_success': '2021-05-27T05: 25: 24.019757259Z',
            'last_error': 'null',
            'disabled': 'false',
            'tags': {
            'server': 'true: 1'},
            'metadata': 'null',
            'retries': 0,
            'dependent_jobs': 'null',
            'parent_job': '',
            'processors': {
            },
            'concurrency': 'allow',
            'executor': 'shell',
            'executor_config': {
            'command': '/bin/true'},
            'status': 'success',
            'next': '2021-05-27T06: 25: 24Z'
        }
    ])
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_active_job_list_response_success():

    server_response = json.dumps([
        {
            'id': '1622311576616995876-ip-172-16-2-146',
            'job_name': 'job2',
            'started_at': '2021-05-29T18: 06: 16.616995876Z',
            'finished_at': '0001-01-01T00: 00: 00Z',
            'success': 'false',
            'node_name': 'ip-172-16-2-146',
            'group': 1622311576597516603,
            'attempt': 1
        },
        {
            'id': '1622311576616995876-ip-172-16-2-146',
            'job_name': 'job3',
            'started_at': '2021-05-29T18: 06: 16.616995876Z',
            'finished_at': '0001-01-01T00: 00: 00Z',
            'success': 'false',
            'node_name': 'ip-172-16-2-146',
            'group': 1622311576597516603,
            'attempt': 1
        }
    ])
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_job_config_response_success():

    server_response = json.dumps({
        'id': 'job',
        'name': 'job',
        'displayname': '',
        'timezone': '',
        'schedule': '@every 1m',
        'owner': 'guy',
        'owner_email': 'guy@bluebatgames.com',
        'success_count': 145154,
        'error_count': 0,
        'last_success': '2021-05-27T01:28:24.035128372Z',
        'last_error': 'null',
        'disabled': 'false',
        'tags': {
            'server':'true:1'
        },
        'metadata': 'null',
        'retries': 0,
        'dependent_jobs': 'null',
        'parent_job': '',
        'processors': {},
        'concurrency': 'allow',
        'executor': 'shell',
        'executor_config': {
            'command':'/bin/true'
        },
        'status': 'success',
        'next': '2021-05-27T01:29:24Z'
    })
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_full_job_history_response_success():

    server_response = json.dumps([
        {
            'id': '1622079204013581868-ip-172-16-2-146',
            'job_name': 'job',
            'started_at': '2021-05-27T01:33:24.013581868Z',
            'finished_at': '2021-05-27T01:33:24.018975352Z',
            'success': 'true',
            'node_name': 'ip-172-16-2-146',
            'group': 1622079204001268640,
            'attempt':2
        },
        {
            'id': '1622079204013581868-ip-172-16-2-147',
            'job_name': 'job',
            'started_at': '2021-05-27T01:33:24.013581869Z',
            'finished_at': '2021-05-27T01:33:24.018975353Z',
            'success': 'false',
            'node_name': 'ip-172-16-2-147',
            'group': 1622079204001268640,
            'attempt':1
        }
    ])
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_limited_job_history_response_success():

    server_response = json.dumps([
        {
            'id': '1622079204013581868-ip-172-16-2-146',
            'job_name': 'job',
            'started_at': '2021-05-27T01:33:24.013581868Z',
            'finished_at': '2021-05-27T01:33:24.018975352Z',
            'success': 'true',
            'node_name': 'ip-172-16-2-146',
            'group': 1622079204001268640,
            'attempt':2
        }
    ])
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_create_job_with_overwrite_response_success():

    server_response = json.dumps(
        {
            'id': 'job',
            'name': 'job',
            'displayname': '',
            'timezone': '',
            'schedule': '0 */15 * * * *',
            'owner': '',
            'owner_email': '',
            'success_count': 145693,
            'error_count': 0,
            'last_success': '2021-05-29T22: 16: 07.018850696Z',
            'last_error': 'null',
            'disabled': 'false',
            'tags': {
                'server': 'true: 1'
            },
            'metadata': 'null',
            'retries': 0,
            'dependent_jobs': 'null',
            'parent_job': '',
            'processors': {},
            'concurrency': 'allow',
            'executor': 'shell',
            'executor_config': {
                'command': '/bin/echo "hello world"',
                'cwd': '/tmp'
            },
            'status': 'success',
            'next': '2021-05-29T22: 17: 07Z'
        }
    )
    return (MockedReponse(server_response), {"status": 201})


def cluster_query_empty_dict_response():

    server_response = json.dumps({})
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_empty_list_response():

    server_response = json.dumps([])
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_response_http_not_found():

    server_response = None
    return (MockedReponse(server_response), {"status": 404})


def cluster_query_response_http_server_error():

    server_response = None
    return (MockedReponse(server_response), {"status": 500})