import document_processor as doc
import documents_processor as docs
import api_call_management as man
import requests
import json
import zipfile
import os
import time
import logging


# These variables are specific to the current implementation
version = "v1.1"
serverurl = "http://10.76.100.34:5000"
home = os.getenv("HOME")
with open(home + '/.env/regulationskey.txt') as f:
    key = f.readline().strip()
    client_id = f.readline().strip()

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='client.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': client_id}
logger = logging.getLogger('tcpserver')


def get_work(client_id):
    """
    Calls the /get_work endpoint of the server to fetch work to process
    :param client_id: the id of the client calling /get_work
    :return: the result of making a call to get work
    """
    global d
    logger.warning('Call Successful: %s', 'get_work: call made successfully', extra=d)
    logger.warning('Assign Variable: %s', 'get_work: create the url for getting work', extra=d)
    url = serverurl+"/get_work?client_id="+str(client_id)
    logger.warning('Variable Success: %s', 'get_work: url created successfully for get work', extra=d)
    logger.warning('Returning: %s', 'get_work: the respond from the api call to get_work', extra=d)
    return man.api_call_manager(url)


def get_json_info(json_result):
    """
    Return job information from server json
    :param json_result: the json returned from
    :return:
    """
    global d
    logger.warning('Call Successful: %s', 'get_json_info: call made successfully', extra=d)
    logger.warning('Assign Variable: %s', 'get_json_info: get the job id from ', extra=d)
    job_id = json_result["job_id"]
    logger.warning('Variable Success: %s', 'get_json_info: job_id retrieved from result json', extra=d)
    logger.warning('Assign Variable: %s', 'get_json_info: get the data from get work endpoint', extra=d)
    urls = json_result["data"]
    logger.warning('Variable Success: %s', 'get_json_info: data retrieved from result json', extra=d)
    logger.warning('Returning: %s', 'get_json_info: returning job id and data from get work', extra=d)
    return job_id, urls

def return_docs(json_result, client_id):
    """
    Handles the documents processing necessary for a job
    Calls the /return_docs endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :param client_id: the id of the client that is processing the documents job
    :return: result from calling /return_docs
    """
    global d
    logger.warning('Call Successful: %s', 'return_docs: call made successfully', extra=d)

    logger.warning('Calling Function: %s','return_docs: call get_json_info for job id and urls',extra=d)
    job_id, urls = get_json_info(json_result)
    logger.warning('Function Successful: %s', 'return_docs: job_id and urls retrieved successfully', extra=d)
    logger.warning('Calling Function: %s','return_docs: call documents_processor',extra=d)
    json = docs.documents_processor(urls,job_id,client_id)
    logger.warning('Function Successful: %s', 'return_docs: successful call to documents processor', extra=d)
    logger.warning('Calling Function: %s','return_docs: post to /return_docs endpoint',extra=d)
    r = requests.post(serverurl+"/return_docs", data=dict(json=json))
    logger.warning('Function Successful: %s', 'return_docs: successful call to /return_docs', extra=d)
    logger.warning('Calling Function: %s','return_docs: Raise Exception for bad status code',extra=d)
    r.raise_for_status()
    logger.warning('Returning: %s', 'return_docs: returning information from the call to /return_docs', extra=d)
    return r


def return_doc(json_result, client_id):
    """
    Handles the document processing necessary for a job
    Calls the /return_doc endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :param client_id: the id of the client that is processing the documents job
    :return: result from calling /return_doc
    """
    global d
    logger.warning('Call Successful: %s', 'return_doc: call made successfully', extra=d)
    logger.warning('Calling Function: %s','return_doc: call get_json_info for job id and urls',extra=d)
    job_id, doc_dicts = get_json_info(json_result)
    logger.warning('Function Successful: %s', 'return_doc: job_id and document ids retrieved successfully', extra=d)
    logger.warning('Assign Variable: %s', 'return_doc: attempting to get document ids from each json', extra=d)
    doc_ids = []
    for dic in doc_dicts:
        logger.warning('Assign Variable: %s', 'return_doc: attempting to get each document id from each json', extra=d)
        doc_ids.append(dic['id'])
        logger.warning('Variable Success: %s', 'return_doc: document id added to the list', extra=d)
    logger.warning('Variable Success: %s', 'return_doc: list of document ids was created', extra=d)
    logger.warning('Calling Function: %s', 'return_doc: create result.zip as storage for data files', extra=d)
    result = zipfile.ZipFile("result.zip", 'w', zipfile.ZIP_DEFLATED)
    logger.warning('Function Successful: %s', 'return_doc: result.zip created successfully', extra=d)
    logger.warning('Calling Function: %s', 'return_doc: call document_processor with the list of document ids', extra=d)
    path = doc.document_processor(doc_ids)
    logger.warning('Function Successful: %s', 'return_doc: document_processor executed successfully', extra=d)
    logger.warning('Calling Function: %s', 'return_doc: walk through every file in the directory to compress all files into results.zip', extra=d)
    for root, dirs, files in os.walk(path.name):
        for file in files:
            logger.warning('Calling Function: %s', 'return_doc: write each file to zip file', extra=d)
            result.write(os.path.join(root, file))
            logger.warning('Function Successful: %s', 'return_doc: file written to zip file', extra=d)
    logger.warning('Function Successful: %s', 'return_doc: all files written to zip file', extra=d)
    logger.warning('Calling Function: %s', 'return_doc: clean up the data in the directory', extra=d)
    path.cleanup()
    logger.warning('Function Successful: %s', 'return_doc: successful cleanup in the directory', extra=d)
    logger.warning('Calling Function: %s','return_doc: post to /return_doc endpoint',extra=d)
    r = requests.post(serverurl+"/return_doc", files={'file':result.extractall()},
                      data={'json':json.dumps({"job_id" : job_id, "type" : "doc", "client_id": client_id, "version" : version })})

    logger.warning('Function Successful: %s', 'return_doc: successful call to /return_doc', extra=d)
    logger.warning('Calling Function: %s','return_doc: Raise Exception for bad status code',extra=d)
    r.raise_for_status()
    logger.warning('Returning: %s', 'return_doc: returning information from the call to /return_docs', extra=d)
    return r


def do_work():
    """
    Working loop
    Get work - Determine type of work - Do work - Return work
    If there is no work in the server, sleep for an hour
    :return:
    """
    logger.warning('Call Successful: %s', 'do_work: called successfully', extra=d)
    while True:
        logger.warning('Calling Function: %s', 'do_work: call to get_work function', extra=d)
        work = get_work(client_id)
        logger.warning('Function Successful: %s', 'do_work: get_work call successful', extra=d)
        logger.warning('Assign Variable: %s', 'do_work: decode the json variable from get_work', extra=d)
        work_json = json.loads(work.content.decode('utf-8'))
        logger.warning('Variable Success: %s', 'do_work: decode the json of work successfully', extra=d)
        if work_json["type"] == "doc":
            logger.warning('Calling Function: %s', 'do_work: call return_doc', extra=d)
            r = return_doc(work_json, client_id)
            logger.warning('Function Successful: %s', 'do_work: return_doc call successful', extra=d)
        elif work_json["type"] == "docs":
            logger.warning('Calling Function: %s', 'do_work: call return_docs', extra=d)
            r = return_docs(work_json, client_id)
            logger.warning('Function Successful: %s', 'do_work: return_docs call successful', extra=d)
        elif work_json["type"] == "none":
            logger.warning('Function Successful: %s', 'do_work: sleep due to no work', extra=d)
            time.sleep(3600)
        else:
            logger.warning('Exception: %s', 'do_work: type specified in json object was not in - doc, docs, none')
        logger.warning('Function Successful: %s', 'do_work: successful iteration in do work', extra=d)


if __name__ == '__main__':
    do_work()
