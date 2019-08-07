from flask import Flask, request, abort

app = Flask(__name__)
@app.route("/")
def home():
    return "Hello, Flask!"

from step3_5_large_interactive_message import app as step3_5
from step3_5_large_interactive_message import receive_large_interactive_payload
from step2_1_send_image_attachment import send_message_with_image_attachment

# exec(open('step3_5_large_interactive_message.py').read())
# from .step3_5_large_interactive_message import receive_large_interactive_payload
app.route("/message", methods=['POST'])(receive_large_interactive_payload)
app.route("/sendattachment", methods=['POST'])(send_message_with_image_attachment)

# app.run(host='127.0.0.1', port=8002)

# def landingPage():
#     return render_template("landingPage.html")
