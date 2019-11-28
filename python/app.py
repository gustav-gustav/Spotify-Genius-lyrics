import os, time, io, datetime, json
from flask import Flask, render_template, request, render_template_string

app = Flask(__name__)
app.template_folder = os.path.join(os.environ['LYRICS_PATH'], 'templates')
app.static_folder = os.path.join(os.environ['LYRICS_PATH'], 'templates', 'static')

base_path = os.environ['LYRICS_PATH']
json_path = os.path.join(base_path, 'json')

@app.route("/")
def test():
    return render_template('test.html')
    # return render_template("home.html", lyrics=reader())

@app.route('/data')
def data():
    return reader()

def reader():
    global base_path
    global json_path

    with io.open(os.path.join(json_path, 'spotify.json'), 'r') as f:
        js = json.load(f)
        js_url = js["item"]["album"]["images"][0]["url"]

    with io.open(os.path.join(base_path, 'lyrics.txt'), 'r') as f:
        HEAD = f.readline().strip("\n")
        LYRICS = f.read().replace('\n', '<br>')

    lyrics = {"HEAD": HEAD, "LYRICS": LYRICS, 'IMAGE': js_url}
    return lyrics


if __name__ == "__main__":
    app.run("0.0.0.0", debug=1)
