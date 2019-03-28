import json
import shutil
import tempfile
import time

import mirrulations_core.config as config

from mirrulations_core.api_call_manager import APICallManager
from mirrulations_client.client_health_call_manager import ClientHealthCallManager
from mirrulations_client.server_call_manager import ServerCallManager

import mirrulations_client.document_processor as doc
import mirrulations_client.documents_processor as docs

from mirrulations_core import VERSION, LOGGER


def do_work(work_json):

    work_type = work_json['type']

    if work_type in ['doc', 'docs', 'none']:

        if work_type == 'none':
            LOGGER.info('No work, sleeping...')
            time.sleep(3600)
        else:
            LOGGER.info('Work is ' + work_type + ' job')

            if work_type == 'doc':
                return_doc(work_json)
            else:
                return_docs(work_json)

        ClientHealthCallManager().make_call()

    else:
        LOGGER.error('Job type unexpected')
        ClientHealthCallManager().make_fail_call()


def return_docs(json_result):
    """
    Handles the documents processing necessary for a job
    Calls the /return_docs endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :return: result from calling /return_docs
    """

    job_id = json_result['job_id']
    data = json_result['data']
    json_info = docs.documents_processor(APICallManager('CLIENT'),
                                         data,
                                         job_id,
                                         config.read_value('CLIENT', 'client_id'))
    path = tempfile.TemporaryDirectory()
    shutil.make_archive('result', 'zip', path.name)
    file_obj = open('result.zip', 'rb')
    r = ServerCallManager().make_docs_return_call(file_obj, json_info)
    r.raise_for_status()
    return r


def return_doc(json_result):
    """
    Handles the document processing necessary for a job
    Calls the /return_doc endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :return: result from calling /return_doc
    """

    job_id = json_result['job_id']
    doc_dicts = json_result['data']
    doc_ids = []
    for dic in doc_dicts:
        doc_ids.append(dic['id'])
    path = doc.document_processor(APICallManager('CLIENT'), doc_ids)
    shutil.make_archive('result', 'zip', path.name)
    file_obj = open('result.zip', 'rb')
    json_info = {'job_id': job_id,
                 'type': 'doc',
                 'user': config.read_value('CLIENT', 'client_id'),
                 'version': VERSION}
    r = ServerCallManager().make_doc_return_call(file_obj, json_info)
    r.raise_for_status()
    return r


def run():
    """
    Working loop
    Get work - Determine type of work - Do work - Return work
    If there is no work in the server, sleep for an hour
    """

    while True:

        try:
            work = ServerCallManager().make_work_call()
        except APICallManager.CallFailException:
            LOGGER.debug('API Call Failed...')
            LOGGER.info('Waiting an hour until retry...')
            time.sleep(3600)
            continue

        ClientHealthCallManager().make_call()
        work_json = json.loads(work.content.decode('utf-8'))
        work_json_dict = {'job_id': work_json[0],
                          'type': work_json[1],
                          'data': work_json[2]}

        do_work(work_json_dict)