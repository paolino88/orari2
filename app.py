from flask import Flask, render_template
from tabula import read_pdf
import urllib.request
import pandas as pd
import numpy as np
import datetime
import re
import os

app = Flask(__name__)

@app.route('/')

def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)