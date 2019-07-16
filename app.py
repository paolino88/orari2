from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    animal = 'dog'
    return render_template("index.html", value=animal)





if __name__ == '__main__': app.run(debug=True)