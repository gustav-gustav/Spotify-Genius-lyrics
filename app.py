import os, time, io
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def test():
    while True:
        with io.open('lyrics.txt', 'r') as f:
            HEAD = f.readline().strip("\n")
            BODY = f.read().split('\n')

        lyrics = {"HEAD": HEAD, "BODY": BODY}
        return render_template("home.html", lyrics=lyrics)


if __name__ == "__main__":
    app.run(debug=1)
