from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    dict = {'A' : '100', 'B' : '500'}
    return render_template("index.html", post=dict )





if __name__ == '__main__': app.run(debug=True)