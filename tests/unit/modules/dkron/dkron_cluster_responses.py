import json


class MockedReponse(object):
    def __init__(self, data):
        self.data = data

    def read(self):
        return self.data


def cluster_query_status_response_success():
    server_response = json.dumps({"cluster_info": {"status": {
        "coordinate_resets": 0,
        "encrypted": False,
        "event_queue": 0,
        "event_time": 1,
        "failed": 0,
        "health_score": 0,
        "intent_queue": 0,
        "left": 0,
        "member_time": 2,
        "members": 2,
        "query_queue": 0,
        "query_time": 1
    }}})
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_leader_response_success():
    server_response = json.dumps({"leader": "172.16.0.1"})
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_members_response_success():
    server_response = json.dumps({"members": [
    	"172.16.0.1",
    	"172.16.0.2",
    	"172.16.0.3"
    ]})
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_job_list_response_success():
    server_response = json.dumps({"jobs": [
    	"testjob1",
    	"testjob2",
    	"testjob3"
    ]})
    return (MockedReponse(server_response), {"status": 200})


def cluster_query_response_http_not_found():
    server_response = None
    return (MockedReponse(server_response), {"status": 404})


def cluster_query_response_http_server_error():
    server_response = None
    return (MockedReponse(server_response), {"status": 500})