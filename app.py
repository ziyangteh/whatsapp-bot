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
    
    # Handle state-based text responses
    if user_session['state'] is not None:
        result = handle_text_response(incoming_msg, user_session, msg)
        if result:
            return result
    
    # Handle "0" or "menu" to return to main menu
    if incoming_msg in ['0', 'menu', 'main menu', 'restart', 'start over']:
        user_session['state'] = None
        user_session['data'] = {}
        msg.body("🏠 *Main Menu:*\n\n• Buy Property\n• Rent Property\n• Market Prices\n• Investment Advice\n• Book Viewing\n• Contact Info\n\n💡 *Just type what you need*")
        return str(resp)
    
    # Greeting responses
    if any(word in incoming_msg for word in ['hi', 'hello', 'hey', 'start']):
        user_session['state'] = None  # Reset state
        msg.body("🏠 Hello! I'm Sarah, your property consultant assistant.\n\n*Please choose an option:*\n\n• Buy Property\n• Rent Property\n• Get Market Prices\n• Investment Advice\n• Book Viewing\n• Contact Me\n\n💡 *Just type what you need* (e.g., 'buy', 'rent', 'prices')")
    
    # Property search queries
    elif any(word in incoming_msg for word in ['buy', 'purchase', 'looking for', 'find', 'search']) or incoming_msg == '1':
        user_session['state'] = 'buying'
        msg.body("🔍 Great! Let's find your perfect property.\n\n*What type are you looking for?*\n\n• Apartment/Condo\n• Landed House\n• Commercial Space\n• Investment Property\n\n💡 *Just type the property type*")
    
    # Rental queries  
    elif any(word in incoming_msg for word in ['rent', 'rental', 'lease', 'tenant']) or incoming_msg == '2':
        user_session['state'] = 'renting'
        msg.body("🏡 Perfect! Let's find you a rental.\n\n*What are you looking for?*\n\n• Residential Rental\n• Commercial Space\n• Short-term Stay\n• Room Rental\n\n💡 *Just describe what you need*")
    
    # Price and valuation queries
    elif any(word in incoming_msg for word in ['price', 'cost', 'value', 'worth', 'market']) or incoming_msg == '3':
        user_session['state'] = 'pricing'
        msg.body("💰 I can help with property prices!\n\n*Choose your area:*\n\n• Kuala Lumpur\n• Selangor\n• Penang\n• Johor\n• Other Area\n\n💡 *Just type your area name*")
    
    # Investment advice
    elif any(word in incoming_msg for word in ['invest', 'investment', 'roi', 'return', 'profit']) or incoming_msg == '4':
        user_session['state'] = 'investment'
        msg.body("📈 Smart thinking! Investment help:\n\n*What interests you?*\n\n• Best Investment Areas\n• Calculate ROI\n• Investment Tips\n• Market Trends\n\n💡 *Tell me what you'd like to know*")
    
    # Appointment booking
    elif any(word in incoming_msg for word in ['viewing', 'appointment', 'visit', 'see', 'tour']) or incoming_msg == '5':
        user_session['state'] = 'booking'
        msg.body("📅 Let's book your viewing!\n\n*When works best?*\n\n• This Week\n• Next Week\n• Weekends Only\n• Specific Date\n\n💡 *Tell me your preferred time*")
    
    # Contact and services
    elif any(word in incoming_msg for word in ['contact', 'call', 'whatsapp', 'email', 'reach']) or incoming_msg == '6':
        msg.body("📞 Here's how to reach me:\n\n• *WhatsApp:* +60 12-345 6789\n• *Email:* sarah@propertypro.my\n• *Office:* +60 3-1234 5678\n\n*Available:* Mon-Sat, 9AM-7PM\n\n💡 *Type 'menu' or '0' to return to main options*")
    
    # Help menu
    elif 'help' in incoming_msg:
        msg.body("🏠 *Main Menu:*\n\n• Buy Property\n• Rent Property\n• Market Prices\n• Investment Advice\n• Book Viewing\n• Contact Info\n\n💡 *How to respond:*\n• Type what you want (e.g., 'buy condo')\n\n_Commands: 'menu', 'restart', 'help'_")
    
    # Goodbye
    elif any(word in incoming_msg for word in ['bye', 'goodbye', 'thanks', 'thank you']):
        user_session['state'] = None  # Reset session
        msg.body("🙏 Thank you for choosing our property services!\n\n*Quick actions:*\n• Type 'hi' to start again\n• Type 'contact' for my details\n\nHave a wonderful day! 🏠✨")
    
    # Default response with options
    else:
        msg.body("🤔 I'd love to help you with that!\n\n*Quick Menu:*\n\n• Buy Property\n• Rent Property\n• Get Prices\n• Investment Help\n• Book Viewing\n• Contact Me\n\n💡 *Easy ways to respond:*\n• *Type keywords* (buy, rent, prices, etc.)\n• *Ask anything* - I'll do my best to help!")

    return str(resp)

def handle_numbered_choice(choice, user_session, msg):
    """Handle numbered menu choices based on current state"""
    choice_num = int(choice)
    resp = MessagingResponse()
    
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
            msg.body(f"✅ {property_types[choice_num]} selected!\n\n*Which area interests you?*\n\n• KL City Center\n• Selangor (PJ/Subang)\n• Penang\n• Johor Bahru\n• Other Area\n\n*Just type the area name*")
    
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
            msg.body(f"🎯 Perfect! Looking for *{property_type}* in *{location}*\n\n*What's your budget range?*\n\n• Under RM500k\n• RM500k - RM1M\n• RM1M - RM2M\n• Above RM2M\n• I need advice\n\n*Just type your budget or range*")
            user_session['state'] = 'buy_budget'
    
    elif user_session['state'] == 'renting':
        rental_types = {
            1: "Residential Rental",
            2: "Commercial Space",
            3: "Short-term Stay", 
            4: "Room Rental"
        }
        if choice_num in rental_types:
            user_session['data']['rental_type'] = rental_types[choice_num]
            user_session['state'] = 'rent_budget'
            msg.body(f"🏡 {rental_types[choice_num]} - great choice!\n\n*Monthly budget range?*\n\n• Under RM1,500\n• RM1,500 - RM3,000\n• RM3,000 - RM5,000\n• Above RM5,000\n\n_I'll find the best options for you!_")
    
    elif user_session['state'] == 'pricing':
        areas = {
            1: ("Kuala Lumpur", "RM800-2000/sqft"),
            2: ("Selangor", "RM400-800/sqft"),
            3: ("Penang", "RM500-1200/sqft"),
            4: ("Johor", "RM300-600/sqft")
        }
        if choice_num in areas:
            area, price = areas[choice_num]
            msg.body(f"💰 *{area} Property Prices:*\n\n📊 Average: {price}\n\n*Want specific info?*\n\n• Condo prices\n• Landed house prices\n• Rental rates\n• Get property valuation\n\n*Just tell me what you'd like to know*")
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
    
    return str(resp)

def handle_main_menu_choice(choice, user_session, msg):
    """Handle main menu selections"""
    resp = MessagingResponse()
    
    if choice == "buy":
        user_session['state'] = 'buying'
        msg.body("🔍 Great! Let's find your perfect property.\n\n*What type are you looking for?*\n\n• Apartment/Condo\n• Landed House\n• Commercial Space\n• Investment Property\n\n💡 *Just type the property type*")
    
    elif choice == "rent":
        user_session['state'] = 'renting'
        msg.body("🏡 Perfect! Let's find you a rental.\n\n*What are you looking for?*\n\n• Residential Rental\n• Commercial Space\n• Short-term Stay\n• Room Rental\n\n💡 *Just describe what you need*")
    
    elif choice == "price":
        user_session['state'] = 'pricing'
        msg.body("💰 I can help with property prices!\n\n*Choose your area:*\n\n• Kuala Lumpur\n• Selangor\n• Penang\n• Johor\n• Other Area\n\n💡 *Just type your area name*")
    
    elif choice == "invest":
        user_session['state'] = 'investment'
        msg.body("📈 Smart thinking! Investment help:\n\n*What interests you?*\n\n• Best Investment Areas\n• Calculate ROI\n• Investment Tips\n• Market Trends\n\n💡 *Tell me what you'd like to know*")
    
    elif choice == "viewing":
        user_session['state'] = 'booking'
        msg.body("📅 Let's book your viewing!\n\n*When works best?*\n\n• This Week\n• Next Week\n• Weekends Only\n• Specific Date\n\n💡 *Tell me your preferred time*")
    
    elif choice == "contact":
        msg.body("📞 Here's how to reach me:\n\n• *WhatsApp:* +60 12-345 6789\n• *Email:* sarah@propertypro.my\n• *Office:* +60 3-1234 5678\n\n*Available:* Mon-Sat, 9AM-7PM\n\n💡 *Type 'menu' or '0' to return to main options*")
    
    return str(resp)

def handle_text_response(incoming_msg, user_session, msg):
    """Handle text-based responses based on current state"""
    resp = MessagingResponse()
    
    if user_session['state'] == 'buying':
        # Handle property type selection
        property_types = ["apartment", "condo", "apartment/condo", "house", "landed", "landed house", 
                         "commercial", "commercial space", "investment", "investment property"]
        
        if any(prop_type in incoming_msg for prop_type in ["apartment", "condo", "apartment/condo"]):
            user_session['data']['property_type'] = "Apartment/Condo"
            user_session['state'] = 'buy_location'
            msg.body("✅ Apartment/Condo selected!\n\n*Which area interests you?*\n\n• KL City Center\n• Selangor (PJ/Subang)\n• Penang\n• Johor Bahru\n• Other Area\n\n*Just type the area name*")
            return str(resp)
            
        elif any(prop_type in incoming_msg for prop_type in ["house", "landed", "landed house"]):
            user_session['data']['property_type'] = "Landed House"
            user_session['state'] = 'buy_location'
            msg.body("✅ Landed House selected!\n\n*Which area interests you?*\n\n• KL City Center\n• Selangor (PJ/Subang)\n• Penang\n• Johor Bahru\n• Other Area\n\n*Just type the area name*")
            return str(resp)
            
        elif any(prop_type in incoming_msg for prop_type in ["commercial", "commercial space"]):
            user_session['data']['property_type'] = "Commercial Space"
            user_session['state'] = 'buy_location'
            msg.body("✅ Commercial Space selected!\n\n*Which area interests you?*\n\n• KL City Center\n• Selangor (PJ/Subang)\n• Penang\n• Johor Bahru\n• Other Area\n\n*Just type the area name*")
            return str(resp)
            
        elif any(prop_type in incoming_msg for prop_type in ["investment", "investment property"]):
            user_session['data']['property_type'] = "Investment Property"
            user_session['state'] = 'buy_location'
            msg.body("✅ Investment Property selected!\n\n*Which area interests you?*\n\n• KL City Center\n• Selangor (PJ/Subang)\n• Penang\n• Johor Bahru\n• Other Area\n\n*Just type the area name*")
            return str(resp)
    
    elif user_session['state'] == 'buy_location':
        # Handle location selection
        locations = {
            "kl": "KL City Center",
            "kuala lumpur": "KL City Center",
            "selangor": "Selangor (PJ/Subang)",
            "pj": "Selangor (PJ/Subang)",
            "subang": "Selangor (PJ/Subang)",
            "penang": "Penang",
            "johor": "Johor Bahru",
            "johor bahru": "Johor Bahru"
        }
        
        for key, location in locations.items():
            if key in incoming_msg:
                property_type = user_session['data'].get('property_type', 'Property')
                user_session['data']['location'] = location
                user_session['state'] = 'buy_budget'
                msg.body(f"🎯 Perfect! Looking for *{property_type}* in *{location}*\n\n*What's your budget range?*\n\n• Under RM500k\n• RM500k - RM1M\n• RM1M - RM2M\n• Above RM2M\n• I need advice\n\n*Just type your budget or range*")
                return str(resp)
    
    # Add more state handlers as needed
    
    return None  # Return None if no matching handler found

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
