from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Simple session storage (use Redis/database in production)
user_sessions = {}

@app.route("/bot", methods=['GET', 'POST'])
def bot():
    if request.method == 'GET':
        return "I'm alive!", 200

    incoming_msg = request.values.get('Body', '').strip().lower()
    user_phone = request.values.get('From', '')  # Get user's phone number for session tracking
    resp = MessagingResponse()
    msg = resp.message()
    
    # Get or create user session
    if user_phone not in user_sessions:
        user_sessions[user_phone] = {'state': None, 'data': {}}

    user_session = user_sessions[user_phone]
    
    # Handle numbered responses first
    if incoming_msg.isdigit():
        return handle_numbered_choice(incoming_msg, user_session, msg)
    
    # Handle "0" or "menu" to return to main menu
    if incoming_msg in ['0', 'menu', 'main menu', 'restart', 'start over']:
        user_session['state'] = None
        user_session['data'] = {}
        msg.body("🏠 *Main Menu:*\n\n1️⃣ Buy Property\n2️⃣ Rent Property\n3️⃣ Market Prices\n4️⃣ Investment Advice\n5️⃣ Book Viewing\n6️⃣ Contact Info\n\n💡 *Reply with number (1-6) or type what you need*")
        return str(resp)
    
    # Greeting responses
    if any(word in incoming_msg for word in ['hi', 'hello', 'hey', 'start']):
        user_session['state'] = None  # Reset state
        msg.body("🏠 Hello! I'm Sarah, your property consultant assistant.\n\n*Please choose an option:*\n\n1️⃣ Buy Property\n2️⃣ Rent Property  \n3️⃣ Get Market Prices\n4️⃣ Investment Advice\n5️⃣ Book Viewing\n6️⃣ Contact Me\n\n💡 *You can reply with:*\n• *Number* (1-6) - Quick & easy!\n• *Text* (e.g., 'buy', 'rent', 'prices')")
    
    # Property search queries
    elif any(word in incoming_msg for word in ['buy', 'purchase', 'looking for', 'find', 'search']) or incoming_msg == '1':
        user_session['state'] = 'buying'
        msg.body("🔍 Great! Let's find your perfect property.\n\n*What type are you looking for?*\n\n1️⃣ Apartment/Condo\n2️⃣ Landed House\n3️⃣ Commercial Space\n4️⃣ Investment Property\n\n💡 *Reply with number (1-4) or type the property type*")
    
    # Rental queries  
    elif any(word in incoming_msg for word in ['rent', 'rental', 'lease', 'tenant']) or incoming_msg == '2':
        user_session['state'] = 'renting'
        msg.body("🏡 Perfect! Let's find you a rental.\n\n*What are you looking for?*\n\n1️⃣ Residential Rental\n2️⃣ Commercial Space\n3️⃣ Short-term Stay\n4️⃣ Room Rental\n\n💡 *Reply with number (1-4) or describe what you need*")
    
    # Price and valuation queries
    elif any(word in incoming_msg for word in ['price', 'cost', 'value', 'worth', 'market']) or incoming_msg == '3':
        user_session['state'] = 'pricing'
        msg.body("💰 I can help with property prices!\n\n*Choose your area:*\n\n1️⃣ Kuala Lumpur\n2️⃣ Selangor\n3️⃣ Penang\n4️⃣ Johor\n5️⃣ Other Area\n\n💡 *Reply with number (1-5) or type your area name*")
    
    # Investment advice
    elif any(word in incoming_msg for word in ['invest', 'investment', 'roi', 'return', 'profit']) or incoming_msg == '4':
        user_session['state'] = 'investment'
        msg.body("📈 Smart thinking! Investment help:\n\n*What interests you?*\n\n1️⃣ Best Investment Areas\n2️⃣ Calculate ROI\n3️⃣ Investment Tips\n4️⃣ Market Trends\n\n💡 *Reply with number (1-4) or tell me what you'd like to know*")
    
    # Appointment booking
    elif any(word in incoming_msg for word in ['viewing', 'appointment', 'visit', 'see', 'tour']) or incoming_msg == '5':
        user_session['state'] = 'booking'
        msg.body("📅 Let's book your viewing!\n\n*When works best?*\n\n1️⃣ This Week\n2️⃣ Next Week\n3️⃣ Weekends Only\n4️⃣ Specific Date\n\n💡 *Reply with number (1-4) or tell me your preferred time*")
    
    # Contact and services
    elif any(word in incoming_msg for word in ['contact', 'call', 'whatsapp', 'email', 'reach']) or incoming_msg == '6':
        msg.body("📞 Here's how to reach me:\n\n• *WhatsApp:* +60 12-345 6789\n• *Email:* sarah@propertypro.my\n• *Office:* +60 3-1234 5678\n\n*Available:* Mon-Sat, 9AM-7PM\n\n💡 *Type 'menu' or '0' to return to main options*")
    
    # Help menu
    elif 'help' in incoming_msg:
        msg.body("🏠 *Main Menu:*\n\n1️⃣ Buy Property\n2️⃣ Rent Property\n3️⃣ Market Prices\n4️⃣ Investment Advice\n5️⃣ Book Viewing\n6️⃣ Contact Info\n\n💡 *Two ways to respond:*\n• *Quick:* Just type a number (1-6)\n• *Detailed:* Type what you want (e.g., 'buy condo')\n\n_Commands: 'menu', 'restart', 'help'_")
    
    # Goodbye
    elif any(word in incoming_msg for word in ['bye', 'goodbye', 'thanks', 'thank you']):
        user_session['state'] = None  # Reset session
        msg.body("🙏 Thank you for choosing our property services!\n\n*Quick actions:*\n• Type 'hi' to start again\n• Type 'contact' for my details\n\nHave a wonderful day! 🏠✨")
    
    # Default response with options
    else:
        msg.body("🤔 I'd love to help you with that!\n\n*Quick Menu:*\n\n1️⃣ Buy Property\n2️⃣ Rent Property\n3️⃣ Get Prices\n4️⃣ Investment Help\n5️⃣ Book Viewing\n6️⃣ Contact Me\n\n💡 *Easy ways to respond:*\n• *Type a number* (1-6) - Super quick!\n• *Type keywords* (buy, rent, prices, etc.)\n• *Ask anything* - I'll do my best to help!")

    return str(resp)

def handle_numbered_choice(choice, user_session, msg):
    """Handle numbered menu choices based on current state"""
    choice_num = int(choice)
    
    if user_session['state'] == 'buying':
        property_types = {
            1: "Apartment/Condo",
            2: "Landed House", 
            3: "Commercial Space",
            4: "Investment Property"
        }
        if choice_num in property_types:
            user_session['data']['property_type'] = property_types[choice_num]
            user_session['state'] = 'buy_location'
            msg.body(f"✅ {property_types[choice_num]} selected!\n\n*Which area interests you?*\n\n1️⃣ KL City Center\n2️⃣ Selangor (PJ/Subang)\n3️⃣ Penang\n4️⃣ Johor Bahru\n5️⃣ Other Area\n\n*Reply with number (1-5)*")
    
    elif user_session['state'] == 'buy_location':
        locations = {
            1: "KL City Center",
            2: "Selangor (PJ/Subang)",
            3: "Penang",
            4: "Johor Bahru",
            5: "Other Area"
        }
        if choice_num in locations:
            property_type = user_session['data'].get('property_type', 'Property')
            location = locations[choice_num]
            msg.body(f"🎯 Perfect! Looking for *{property_type}* in *{location}*\n\n*What's your budget range?*\n\n1️⃣ Under RM500k\n2️⃣ RM500k - RM1M\n3️⃣ RM1M - RM2M\n4️⃣ Above RM2M\n5️⃣ I need advice\n\n*Reply with number (1-5)*")
            user_session['state'] = 'buy_budget'
    
    elif user_session['state'] == 'renting':
        rental_types = {
            1: "Residential Rental",
            2: "Commercial Space",
            3: "Short-term Stay", 
            4: "Room Rental"
        }
        if choice_num in rental_types:
            msg.body(f"🏡 {rental_types[choice_num]} - great choice!\n\n*Monthly budget range?*\n\n1️⃣ Under RM1,500\n2️⃣ RM1,500 - RM3,000\n3️⃣ RM3,000 - RM5,000\n4️⃣ Above RM5,000\n\n*Reply with number (1-4)*\n\n_I'll find the best options for you!_")
    
    elif user_session['state'] == 'pricing':
        areas = {
            1: ("Kuala Lumpur", "RM800-2000/sqft"),
            2: ("Selangor", "RM400-800/sqft"),
            3: ("Penang", "RM500-1200/sqft"),
            4: ("Johor", "RM300-600/sqft")
        }
        if choice_num in areas:
            area, price = areas[choice_num]
            msg.body(f"💰 *{area} Property Prices:*\n\n📊 Average: {price}\n\n*Want specific info?*\n\n1️⃣ Condo prices\n2️⃣ Landed house prices\n3️⃣ Rental rates\n4️⃣ Get property valuation\n\n*Reply with number (1-4)*")
        elif choice_num == 5:
            msg.body("📍 *Other Area Pricing*\n\nPlease share your specific area and I'll get you the latest market rates!\n\n_Just type the area name (e.g., 'Ipoh', 'Melaka', 'Kota Kinabalu')_")
    
    # Add more state handlers as needed...
    
    else:
        # Default numbered response - treat as main menu
        main_menu_options = {
            1: "buy",
            2: "rent", 
            3: "price",
            4: "invest",
            5: "viewing",
            6: "contact"
        }
        if choice_num in main_menu_options:
            # Redirect to appropriate handler
            return handle_main_menu_choice(main_menu_options[choice_num], user_session, msg)
    
    return str(MessagingResponse().message(msg.body))

def handle_main_menu_choice(choice, user_session, msg):
    """Handle main menu selections"""
    # This redirects back to the main handlers
    # You can integrate this better by refactoring the main function
    pass

    return str(resp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
