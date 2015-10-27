import os, sys
import argparse
import requests
import json

API_ADDR = "http://52.22.71.167"
OAM_SERVER_TOKEN_ENV = "OAM_SERVER_TOKEN"

REQUESTS_URI = os.path.join(API_ADDR, "requests")
TILE_URI = os.path.join(API_ADDR, "tile")

class NoJobError(Exception):
    def __init__(self, job_id):
        self.job_id = job_id
    def __str__(self):
        return repr(self.job_id)

class NoTokenError(Exception):
    def __init__(self):
        pass

def status_uri(id):
    return os.path.join(API_ADDR, "status", id)

def info_uri(id):
    return os.path.join(API_ADDR, "info", id)

class Job(object):
    def __init__(self, job_id, 
                 request_time = None,
                 status = None,
                 tile_json = None,
                 images = None):
        self.job_id = job_id
        self._request_time = request_time
        
        self._status = status
        self._tile_json = tile_json
        self._images = images

    def update_requests(self):
        job_responses = requests.get(REQUESTS_URI).json()
        job_request = [r for r in job_responses if r["jobId"] == self.job_id]
        if not job_request:
            raise NoJobError(self.job_id)
        self._request_time = job_request[0]["request_time"]
        
    def update_status(self):
        response = requests.get(status_uri(self.job_id)).json()
        self._status = response["status"]
        if "tilejson" in response:
            self._tile_json = response["tilejson"]

    def update_info(self):
        response = requests.get(info_uri(self.job_id)).json()
        self._images = response["images"]

    def request_time(self):
        if not self._request_time:
            self.update_requests()
        return self._request_time

    def status(self):
        # Always update status
        self.update_status()
        return self._status

    def images(self):
        if not self._images:
            self.update_info()
        return self._images

    def tile_json(self):
        if not self._tile_json:
            self.update_status()
        return self._tile_json

def get_jobs():
    job_requests = requests.get(REQUESTS_URI).json()
    jobs = []
    for jr in job_requests:
        jobs.append(Job(jr["jobId"], jr["request_time"]))
    return jobs

def get_job(job_id):
    job_requests = requests.get(REQUESTS_URI).json()
    jobs = []
    for jr in job_requests:
        if jr["jobId"].startswith(job_id):
            return Job(jr["jobId"], jr["request_time"])
    return None

def tile(images):
    token = os.environ.get(OAM_SERVER_TOKEN_ENV)
    if not token:
        raise NoTokenError()
    request = { 'sources' : images }
    r = requests.post(TILE_URI, json=request, params={ 'token': token })

    if r.ok:
        return Job(r.json()["id"])
    else:
        raise Exception(r.status_code)

def handle_jobs(args):
    print "JOB ID\t\t\t\t\t\tREQUEST TIME\t\t\t\tSTATUS"
    for job in reversed(sorted(get_jobs(), key=lambda j: j.request_time())):
        print "%s\t\t%s\t\t%s" % (job.job_id, job.request_time(), job.status())

def handle_info(args):
    job = get_job(args.job_id)

    if not job:
        print "Job ID %s does not exist." % e.job_id
        sys.exit(1)
    else:
        print "JOB ID\t\t\t\t\t\tREQUEST TIME\t\t\t\tSTATUS"
        print "%s\t\t%s\t\t%s" % (job.job_id, job.request_time(), job.status())
        print "\tImages:"
        for img in job.images():
            print "\t%s" % img
        if job.status() == "COMPLETED":
            print
            print json.dumps(job.tile_json(),
                             indent=4, separators=(',', ': '))

def handle_tile(args):
    images = args.images
    if args.file:
        images = filter(lambda x: x, open(images[0]).read().split('\n'))
    try:
        job = tile(images)
        print "Started job with ID: %s" % (job.job_id)
    except NoTokenError:
        print "There is no OAM Server token set. Please set the %s environment variable to your token." % (OAM_SERVER_TOKEN_ENV)
        print "If you do not have a token, contact a HOT administrator to obtain one."
        sys.exit(1)

def main(args):
    parser = argparse.ArgumentParser(prog='PROG')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_tile = subparsers.add_parser('jobs', help='List jobs.')
    parser_tile.set_defaults(func=handle_jobs)

    parser_info = subparsers.add_parser('info', help='Get info about a job.')
    parser_info.add_argument('job_id', metavar='JOB_ID', type=str,
                   help='Job ID of job to get infomation about.')
    parser_info.set_defaults(func=handle_info)

    parser_tile = subparsers.add_parser('tile', help='Kick off a tiling job.')
    parser_tile.add_argument('images', metavar='IMAGE_URI', type=str, nargs='+',
                   help='Images to tile, or path to file of image URIs if -f is supplied')
    parser_tile.add_argument('-f', '--file', action='store_true',
                   help="This flag specifies that a file path will be given instead of an image list; that file contains image URI's, one per line.")
    parser_tile.set_defaults(func=handle_tile)

    parsed_args = parser.parse_args(args)
    parsed_args.func(parsed_args)

if __name__ == "__main__":
    main(sys.argv)
