from datetime import datetime, timedelta
from enum import Enum, unique
from urllib.parse import urljoin
from uuid import uuid4

from flask import Flask, jsonify, request
from rq.exceptions import NoSuchJobError
from rq.job import Job, cancel_job

from tasks.base import queue
from tasks.finder import find_trains

import settings

app = Flask(__name__)

HARD_JOB_DEADLINE = timedelta(hours=settings.JOB_TOTAL_TIMEOUT)

CANCELLED_JOBS = set()
JOBS_CREATION_TIMESTAMP = {}


@unique
class ResponseStatus(Enum):
    OK = 'OK'
    FAIL = 'FAIL'


@app.errorhandler(500)
def server_error(e):
    return jsonify(error=500, text=str(e)), 500


@app.route('/')
def index():
    return 'OK'


@app.route('/cancel/', methods=['POST'])
def cancel():
    data = request.json
    job_id = data['job_id']

    if job_id in CANCELLED_JOBS:
        return jsonify({'status': ResponseStatus.FAIL.value, 'reason': 'Job is already cancelled.'})

    try:
        cancel_job(job_id, connection=queue.connection)
    except NoSuchJobError:
        return jsonify({'status': ResponseStatus.FAIL.value, 'reason': 'Job was not found'})

    CANCELLED_JOBS.add(job_id)

    return jsonify({'status': ResponseStatus.OK.value, 'reason': None})


@app.route('/retry/', methods=['POST'])
def retry_job():
    data = request.json
    job_id = data['job_id']

    if job_id in CANCELLED_JOBS:
        return jsonify({'status': ResponseStatus.FAIL.value, 'job_id': None,
                        'reason': 'Job has already been cancelled'})

    if job_id not in JOBS_CREATION_TIMESTAMP:
        JOBS_CREATION_TIMESTAMP[job_id] = datetime.now()

    job_created_at = JOBS_CREATION_TIMESTAMP[job_id]
    if job_created_at + HARD_JOB_DEADLINE < datetime.now():
        return jsonify({'status': ResponseStatus.FAIL.value, 'job_id': job_id,
                        'reason': 'Job is stopped by timeout'})

    job = Job.fetch(job_id, connection=queue.connection)

    queue.enqueue_job(job)

    return jsonify({'status': ResponseStatus.OK.value, 'job_id': job_id, 'reason': None})


@app.route('/check_state/<job_id>/')
def check_job_status(job_id):
    job = Job.fetch(job_id, connection=queue.connection)

    return job.get_status()


@app.route('/find/<kind>/', methods=['POST'])
def find_rw(kind):
    if kind == 'rw':
        data = request.json

        job_id = str(uuid4())

        tg_bot_token = data['tg_bot_token']
        tg_chat_id = data['tg_chat_id']
        crawler = {
            'src': data['crawler_src'],
            'dest': data['crawler_dest'],
            'date': data['crawler_date'],
            'min_seats': data['crawler_min_seats'],
            'train_num': data.get('crawler_train_num'),
            'seat_type': data.get('crawler_seat_type'),
            'lang': data['crawler_lang'],
            'queue_job_id': job_id,
            'retry_url': urljoin(settings.APP_SERVER_URL, '/retry/'),
        }

        queue.enqueue(
            find_trains,
            job_id=job_id,
            tg_bot_token=tg_bot_token,
            tg_chat_id=tg_chat_id,
            job_timeout=settings.JOB_SINGLE_RUN_TIMEOUT,
            **crawler,
        )

        JOBS_CREATION_TIMESTAMP[job_id] = datetime.now()

        return jsonify({'job_id': job_id})

    else:
        raise ValueError(f'{kind} kind is not supported yet.')


if __name__ == '__main__':
    app.run(port=settings.APP_PORT, host='0.0.0.0')
