from flask import Flask, render_template, url_for


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/arancio_andata')
def index_arancia_andata():
    return render_template('arancio_andata.html')




if __name__ == '__main__':
    app.run(use_reloader = True,debug=True)