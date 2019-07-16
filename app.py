from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    index = open("index.html").read().format(first_header='goodbye',p1='World',p2='Hello')
    return render_template(index)





if __name__ == '__main__': app.run(debug=True)