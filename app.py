import os, time, io, datetime, json
from flask import Flask, render_template, request, render_template_string

app = Flask(__name__)

@app.route("/")
def test():
    return render_template('test.html')
    # return render_template("home.html", lyrics=reader())

@app.route('/data')
def data():
    return reader()

def reader():
    with io.open('spotify.json', 'r') as f:
        js = json.load(f)
        js_url = js["item"]["album"]["images"][0]["url"]

    with io.open('lyrics.txt', 'r') as f:
        HEAD = f.readline().strip("\n")
        BODY = f.read().replace('\n', '<br>')

    lyrics = {"HEAD": HEAD, "BODY": BODY, 'IMAGE': js_url}
    return lyrics


if __name__ == "__main__":
    app.run(debug=1)
