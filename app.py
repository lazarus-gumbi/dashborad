import collections
import json
from matplotlib.pyplot import title
import requests
import pygal
import datetime as dt
from flask import Flask, render_template
from pygal.style import DarkStyle
from pygal.style import DefaultStyle

app = Flask(__name__)

@app.route('/daily')
def daily():

    url_sent = ''

    res = requests.get(url_sent)
    data = json.loads(res.content)
    sent = data['data']
    dates = []
    val = []
    labels = []

    for i in sent:
        labels.append(i['Date'])
        d = dt.datetime.strptime(i['Date'],"%d/%m/%Y").date()

        dates.append(d.isoformat())
        val.append(i['TotalSMS'])

    date_line = pygal.Line(title='Daily SMS Data',x_label_rotation=-90,width=500,height=300,show_x_labels=False,legend_at_bottom=True)
    date_line.x_labels = dates

    date_line.add('daily sms data',val)
    graph = date_line.render_data_uri()
    return render_template('daily.html',graph = graph)

@app.route('/')
def hello():
    url = ''

    res = requests.get(url)
    data = json.loads(res.content)
    d = collections.defaultdict(dict)

    months = []
    m = []

    for d in data['data']:

        if d['Month'] not in (m):
            m.append(d['Month'])

            months.append(
                {'month': d['Month'],
                'sent': None if d['SMSStatus'] != 'Sent' else d['TotalSMS'],
                'pending': None if d['SMSStatus'] != 'Pending' else d['TotalSMS'],
                'failed': None if d['SMSStatus'] != 'Failed' else d['TotalSMS']})
        else:
            tom_index = next((index for (index, c) in enumerate(
                months) if c["month"] == d['Month']), None)
            months[tom_index].update({'month': d['Month'],
                                    'sent': d['TotalSMS'] if d['SMSStatus'] == 'Sent' else months[tom_index]['sent'],
                                    'pending': d['TotalSMS'] if d['SMSStatus'] == 'Pending' else months[tom_index]['pending'],
                                    'failed': d['TotalSMS'] if d['SMSStatus'] == 'Failed' else months[tom_index]['failed'], })

    bar = pygal.Bar(width=500,height=280,x_label_rotation=-90)
    bar.title = "Monthly SMS Data"
    bar.x_labels = m
    sent = []
    pending = []
    failed = []

    for i in range(len(m)):
        sent.append(months[i]['sent'])
        pending.append(months[i]['pending'])
        failed.append(months[i]['failed'])

    bar.add('sent', sent)
    bar.add('pending', pending)
    bar.add('failed', failed)
    graph = bar.render_data_uri()

    return render_template('dashboard.html',graph = graph)

if __name__ == '__main__':
    app.run(debug=True)
