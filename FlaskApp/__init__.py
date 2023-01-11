from flask import Flask, render_template


app = Flask(__name__)

@app.route("/")
def index():
    return (
        "Try /hello/Chris for parameterized Flask route.\n"
        "Try /module for module import guidance"
    )

@app.route("/hello/<name>", methods=['GET'])
def hello(name: str):
    return f"hello {name}"

@app.route("/balls/<name>", methods=['GET'])
def balls(name: str):
    return render_template('farts.html', balls=name if name else "hoopla")

@app.route("/module")
def module():
    return f"<h1>Balls</h1>"

if __name__ == "__main__":
    app.run()