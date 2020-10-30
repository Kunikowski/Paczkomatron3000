from flask import Flask, render_template
app = Flask(__name__)
app.debug = False


@app.route('/sender/sign-up')
def sender_signup():
    return render_template("sender_signup.html")

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)