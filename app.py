import os, re, datetime, json, threading, time, requests, unicodedata
from apscheduler.schedulers.background import BackgroundScheduler
#
# import logging
#
# logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)


from flask import Flask, request, abort
from flask_mako import MakoTemplates, render_template

from waitress import serve

app = Flask(__name__)
mako = MakoTemplates(app)

#####
if not os.path.exists('datasets'):
    os.mkdir('datasets')
if not os.path.exists('lists'):
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
            f = Finance('week adj')
            f.get_tickers(tickers)
            f.write_values(os.path.join('datasets', f'{dataset}_{today}.csv'))
            self.slack(f'Finance tickers {dataset} retrieved ({len(tickers)}')
            print('done')

    def slack(self, msg):
        """
        Send message to a slack webhook.
        Copy pasted code from Michelanglo. Obvs nothing malicious is sent from here!
        :param msg:
        :return:
        """
        # sanitise.
        if 'SLACK_WEBHOOK' not in os.environ:
            print('no SLACK_WEBHOOK')
            return False
        msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii')
        msg = re.sub('[^\w\s\-.,;?!@#()\[\]]', '', msg)
        r = requests.post(url=os.environ['SLACK_WEBHOOK'],
                          headers={'Content-type': 'application/json'},
                          data=f"{{'text': 'Irrigator: {msg}'}}")
        if r.status_code == 200 and r.content == b'ok':
            return True
        else:
            print(f'{msg} failed to send (code: {r.status_code}, {r.content}).')
            return False




@app.route('/')
def welcome():
    assert_welcome()
    return render_template('home.mako', name='mako')


def assert_welcome():
    if request.args.get('key') != os.environ['FINANCIAL_KEY']:
        abort(403, description="No access key provided")


@app.route('/download')
def download():
    file = os.path.split(request.args['dataset'])[1]
    if os.path.splitext(file)[1] != '.csv':
        abort(401, description="Dodgy extension!")
    if not os.path.exists(os.path.join('datasets', file)):
        abort(404, description="File not found")
    else:
        return open(os.path.join('datasets', file)).read()

@app.route('/retrieve')
def retrieve():
    assert_welcome()
    tickers = request.args['tickers'].replace(';', '\n').replace(',', '\n').replace(' ', '\n').split('\n')
    tickers = [t for t in tickers if t]
    dataset = re.sub(r'[^\w_\.]','', request.args['name'].replace('.csv', ''))
    today = datetime.datetime.now().date().isoformat()
    with open(os.path.join('lists', f'{dataset}_{today}.json'), 'w') as w:
        json.dump(tickers, w)
    ScheduledFinance(dataset, today, tickers)
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
    serve(app, port=8041)
