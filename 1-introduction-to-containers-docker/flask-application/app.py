from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello world!</h1>'

@app.route('/healthz')
def health():
    return '<h1>Healthy!</h1>'

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8080)