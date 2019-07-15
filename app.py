from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def index():
    flight={'FilghtNum' : 'pippo'}
    return render_template('flight.html', flight=flight)





if __name__ == '__main__': app.run(debug=True)