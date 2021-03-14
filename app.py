import os, re, datetime, json, threading, time, requests, unicodedata
from apscheduler.schedulers.background import BackgroundScheduler

for key in ('ALPHA_KEY', 'FINANCIAL_KEY', 'SLACK_WEBHOOK'):
    if key not in os.environ:
        raise EnvironmentError('Please specify environment variable '+key)

#
# import logging
#
# logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)


from flask import Flask, request, abort
from flask_mako import MakoTemplates, render_template

from waitress import serve

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'logfile': {
                                'class': 'logging.FileHandler',
                                'filename': 'log.log',
                                'level': 'INFO',
                                'formatter': 'default'
                            },'stream': {
                                'class': 'logging.StreamHandler',
                                'level': 'INFO',
                                'formatter': 'default',
                                'stream': 'ext://sys.stdout'
                            }
                },
    'root': {
        'level': 'INFO',
        'handlers': ['logfile', 'stream']
    }
})



app = Flask(__name__)
mako = MakoTemplates(app)

#####
if not os.path.exists('datasets'):
    print('Making folder dataset')
    os.mkdir('datasets')
if not os.path.exists('lists'):
    print('Making folder list')
    os.mkdir('lists')

####################################


from financial_fetcher import Finance

class ScheduledFinance:
    scheduler = BackgroundScheduler()
    scheduler.start()
    lock = threading.Lock()

    def __init__(self, dataset: str, today: str, tickers: list):
        self.scheduler.add_job(func=self.retrieve, args=[dataset, today, tickers])

    def retrieve(self, dataset: str, today: str, tickers: list):
        with self.lock:
            try:
                f = Finance('week adj')
                f.get_tickers(tickers)
                f.write_values(os.path.join('datasets', f'{dataset}_{today}.csv'))
                self.slack(f'Finance tickers {dataset} retrieved ({len(tickers)}')
                app.logger.info(f'done {dataset}_{today}')
            except Exception as error:
                msg = f'failed {dataset}_{today} due to {type(error).__name__}: {error}'
                app.logger.warning(msg)
                self.slack(msg)

    def slack(self, msg):
        """
        Send message to a slack webhook.
        Copy pasted code from Michelanglo. Obvs nothing malicious is sent from here!
        :param msg:
        :return:
        """
        # sanitise.
        if 'SLACK_WEBHOOK' not in os.environ:
            app.logger.warning('no SLACK_WEBHOOK')
            return False
        msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii')
        msg = re.sub('[^\w\s\-.,;?!@#()\[\]]', '', msg)
        r = requests.post(url=os.environ['SLACK_WEBHOOK'],
                          headers={'Content-type': 'application/json'},
                          data=f"{{'text': 'Irrigator: {msg}'}}")
        if r.status_code == 200 and r.content == b'ok':
            return True
        else:
            app.logger.warning(f'{msg} failed to send (code: {r.status_code}, {r.content}).')
            return False




@app.route('/')
def welcome():
    assert_welcome()
    return render_template('home.mako', name='mako')


def assert_welcome():
    if request.json is not None and request.json['key'] == os.environ['FINANCIAL_KEY']:
        return True
    if request.args.get('key') == os.environ['FINANCIAL_KEY']:
        return True
    else:
        app.logger.info('Access forbidden')
        abort(403, description="No access key provided")

def read_data():
    # this is not tested or used.
    if request.json is not None:
        return request.json
    else:
        return request.args

@app.route('/download')
def download():
    file = os.path.split(request.args['dataset'])[1]
    if os.path.splitext(file)[1] != '.csv':
        app.logger.info(f'Dodgy extension: {file}')
        abort(401, description="Dodgy extension!")
    if not os.path.exists(os.path.join('datasets', file)):
        app.logger.info(f'File not found.')
        abort(404, description="File not found")
    else:
        return open(os.path.join('datasets', file)).read()

@app.route('/retrieve', methods=["GET", "POST"])
def retrieve():
    assert_welcome()
    tickers = request.args['tickers'].replace(';', '\n').replace(',', '\n').replace(' ', '\n').split('\n')
    tickers = [t for t in tickers if t]
    dataset = re.sub(r'[^\w_\.]','', request.args['name'].replace('.csv', ''))
    today = datetime.datetime.now().date().isoformat()
    with open(os.path.join('lists', f'{dataset}_{today}.json'), 'w') as w:
        json.dump(tickers, w)
    ScheduledFinance(dataset, today, tickers)
    app.logger.info('Job added.')
    return 'JOB ADDED'

@app.route('/get_tickers')
def get_tickers():
    assert_welcome()
    file = os.path.split(request.args['dataset'])[1] + '.json'
    if not os.path.exists(os.path.join('lists', file)):
        abort(404, description="File not found")
    else:
        return '\n'.join(json.load(open(os.path.join('lists', file))))

if __name__ == '__main__':
    try:
        serve(app, port=8041)
    except Exception as error:
        msg = f'LETHAL: {type(error).__name__}: {error}.'
        print(msg)
        import logging
        logger = logging.getLogger(__name__)
        logger.critical(msg)
        ScheduledFinance.__new__(ScheduledFinance).slack(msg)
