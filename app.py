from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/bot", methods=['POST'])
def bot():
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if 'hi' in incoming_msg or 'hello' in incoming_msg:
        msg.body("Hello! I'm your chatbot. Ask me anything.")
    elif 'price' in incoming_msg:
        msg.body("Our price starts at RM 99/month. Need more details?")
    elif 'help' in incoming_msg:
        msg.body("Type:\n- 'price' for pricing info\n- 'contact' to reach us\n- 'bye' to exit")
    elif 'bye' in incoming_msg:
        msg.body("Goodbye! Have a great day 👋")
    else:
        msg.body("Sorry, I didn't understand. Type 'help' to see options.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
