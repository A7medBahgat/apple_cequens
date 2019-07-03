from flask import Flask
app = Flask(__name__)
@app.route("/")
def home():
    return "Hello, Flask!"

# def landingPage():
#     return render_template("landingPage.html")