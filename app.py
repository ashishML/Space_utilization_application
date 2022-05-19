from flask import Flask
import os
app = Flask(__name__)


app.config['BUCKET_NAME'] = 'space_utilization_application'