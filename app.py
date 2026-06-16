import streamlit as st
import os
import json
from groq import Groq

# ---------------- CONFIG ----------------

st.set_page_config(page_title="CarWala AI", layout="wide")
st.title("🚗 CarWala Pakistan - AI Car Assistant")

# Securely fetch API key from Streamlit Secrets (Production) or local environment fallback
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    # Fallback for local testing (reads from your local .env or system environment variables)
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY! Please configure it in your Streamlit App Secrets.")

client = Groq(api_key=GROQ_API_KEY)
MODEL_ID = "llama-3.1-8b-instant"

# ---------------- LOAD JSON DATABASE ----------------

@st.cache_resource
def load_car_database():
    try:
        with open("cars.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Critical Error: 'cars.json' data file could not be found.")
        return []

cars = load_car_database()

# Convert list → dictionary with normalized keys for robust lookups
car_database = {}
for car in cars:
    car_database[car["plate"].upper()] = car

# ---------------- LLM WITH DATA AWARENESS ----------------

def generate_car_response(user_query):
    database_context = json.dumps(car_database, indent=2)

    system_prompt = f"""
You are Sara, an expert customer support assistant at CarWala Pakistan.

Here is the REAL live inventory database of available vehicles in our showroom:
{database_context}

Rules for Handling Car Availability & Search:
1. When a user asks for a car (e.g., Corolla, Civic, Suzuki, etc.), check the live inventory above.
2. IF THE CAR IS AVAILABLE: 
   - Reply warmly confirming we have it, for example: "Yes, we have multiple Corolla variants available!" 
   - Follow up by explicitly offering to share the images, and instruct the user to type the plate number or ask for the list to see them (e.g., "Would you like me to share the images? Just let me know or type 'show Corolla' to view them instantly!").
3. IF THE CAR IS NOT IN THE INVENTORY (e.g., Mehran, Vitz, etc.):
   - State clearly and politely that we do not currently have that specific car in stock.
4. General Rules:
   - Speak friendly like a showroom sales assistant.
   - DO NOT introduce yourself or say "I am Sara from the customer support department" unless the user explicitly asks an introduction question like "who are you?" or "what is your name?". For general questions, follow-ups, or queries, just assist them directly without repeating your name.
   - If the user explicitly asks about your identity, only then say: "I am Sara from the customer support department. For further queries, you can contact our manager, Ali Huzaifa."
"""

    cleaned_messages = []
    if "messages" in st.session_state:
        for msg in st.session_state.messages[-10:]:
            if "content" in msg:
                cleaned_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                *cleaned_messages,
                {
                    "role": "user",
                    "content": user_query
                }
            ],
            temperature=0.3, 
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error connecting to AI service: {str(e)}"

# ---------------- BUSINESS LOGIC ROUTER ----------------

def handle_special_cases(query):
    q = query.lower().strip()
    clean_query = q.replace("-", "").replace(" ", "")

    has_image_keyword = any(word in q for word in ["image", "photo", "picture", "show", "see", "view"])
    has_all_keyword = any(word in q for word in ["all", "every", "complete", "full", "list"])
    
    # 1. Global Request
    if has_image_keyword and has_all_keyword:
        return {
            "type": "global_car_list",
            "cars": list(car_database.keys())
        }

    # Define fuzzy keyword arrays to catch common spelling errors
    corolla_variants = ["corolla", "carolla", "corola", "gli", "grande", "altis"]
    civic_variants = ["civic", "civik", "oriel", "vtec"]
    suzuki_variants = ["suzuki", "bolan", "every", "vx", "vxr", "ga", "join"]
    cruiser_variants = ["cruiser", "land", "v8", "zx", "prado", "modellista"]

    # Detect active keyword matches in current prompt
    is_corolla = any(v in q for v in corolla_variants)
    is_civic = any(v in q for v in civic_variants)
    is_suzuki = any(v in q for v in suzuki_variants)
    is_cruiser = any(v in q for v in cruiser_variants)

    # 🛑 CRITICAL SAFETY CHECK: If the user explicitly mentions an unavailable vehicle 
    # (like Prius, Mehran, Vitz, etc.), bypass local routing and let the LLM reject it natively.
    all_known_keywords = corolla_variants + civic_variants + suzuki_variants + cruiser_variants + ["all", "every", "complete", "list", "who are you", "introduce"]
    
    # Common out-of-stock vehicle identifiers or general nouns
    unsupported_cars = ["prius", "mehran", "vitz", "alto", "cultus", "wagonr", "swift", "aqua", "yaris", "city"]
    
    # If they mention an unsupported car OR they are asking for images of something that matches NO known local keywords
    if any(unsupported in q for unsupported in unsupported_cars) or (has_image_keyword and not (is_corolla or is_civic or is_suzuki or is_cruiser or has_all_keyword)):
        return None  # Drops down to LLM to process "Sorry, we don't have this car in stock."

    # 2. Context Extraction (Fallback if no explicit car keyword is matched)
    last_mentioned_car = None
    if "messages" in st.session_state:
        for msg in reversed(st.session_state.messages[-4:]):
            if "content" in msg:
                content = msg["content"].lower()
                if any(v in content for v in corolla_variants):
                    last_mentioned_car = "corolla"
                    break
                elif any(v in content for v in civic_variants):
                    last_mentioned_car = "civic"
                    break
                elif any(v in content for v in suzuki_variants):
                    last_mentioned_car = "suzuki"
                    break
                elif any(v in content for v in cruiser_variants):
                    last_mentioned_car = "land_cruiser"
                    break

    # 3. Identity Check
    if "who are you" in q or "introduce yourself" in q:
        return {
            "type": "text",
            "response": "Hi 👋\n\nI am Sara from customer support department. [cite: 13, 99]\n\nFor further queries contact our manager:\nAli Huzaifa. [cite: 13, 99]"
        }
    
    # 4. Context-Driven Brand Filters (Prioritizes current explicit typing over old session states)
    if (is_corolla or (last_mentioned_car == "corolla" and not (is_civic or is_suzuki or is_cruiser))) and has_image_keyword:
        corollas = [p for p, c in car_database.items() if "corolla" in c["brand"].lower() or "corolla" in c["name"].lower()]
        return {"type": "car_list", "cars": corollas, "brand_label": "Corolla"}

    if (is_civic or (last_mentioned_car == "civic" and not (is_corolla or is_suzuki or is_cruiser))) and has_image_keyword:
        civics = [p for p, c in car_database.items() if "civic" in c["brand"].lower() or "civic" in c["name"].lower()]
        return {"type": "car_list", "cars": civics, "brand_label": "Honda Civic"}

    if (is_suzuki or (last_mentioned_car == "suzuki" and not (is_corolla or is_civic or is_cruiser))) and has_image_keyword:
        suzukis = [p for p, c in car_database.items() if "suzuki" in c["brand"].lower() or "suzuki" in c["name"].lower()]
        return {"type": "car_list", "cars": suzukis, "brand_label": "Suzuki"}

    if (is_cruiser or (last_mentioned_car == "land_cruiser" and not (is_corolla or is_civic or is_suzuki))) and has_image_keyword:
        cruisers = [p for p, c in car_database.items() if "cruiser" in c["brand"].lower() or "cruiser" in c["name"].lower() or "land" in c["name"].lower()]
        return {"type": "car_list", "cars": cruisers, "brand_label": "Toyota Land Cruiser"}

    # 5. Fixed Direct License Plate Matching Pattern
    for plate in car_database.keys():
        clean_plate = plate.replace("-", "").upper()
        if clean_plate in clean_query.upper():
            return {
                "type": "car_detail",
                "plate": plate
            }

    # 6. Appointment Route
    buy_words = ["buy", "purchase", "book", "meeting", "appointment", "test drive", "schedule", "register", "reserve", "reservation"]
    if any(word in q for word in buy_words):
        return {
            "type": "appointment"
        }

    return None
    q = query.lower().strip()
    clean_query = q.replace("-", "").replace(" ", "")

    has_image_keyword = any(word in q for word in ["image", "photo", "picture", "show", "see", "view"])
    has_all_keyword = any(word in q for word in ["all", "every", "complete", "full", "list"])
    
    # 1. Global Request
    if has_image_keyword and has_all_keyword:
        return {
            "type": "global_car_list",
            "cars": list(car_database.keys())
        }

    # Define fuzzy keyword arrays to catch common spelling errors
    corolla_variants = ["corolla", "carolla", "corola", "gli", "grande", "altis"]
    civic_variants = ["civic", "civik", "oriel", "vtec"]
    suzuki_variants = ["suzuki", "bolan", "every", "vx", "vxr", "ga", "join"]
    cruiser_variants = ["cruiser", "land", "v8", "zx", "prado", "modellista"]

    # Detect active keyword matches in current prompt
    is_corolla = any(v in q for v in corolla_variants)
    is_civic = any(v in q for v in civic_variants)
    is_suzuki = any(v in q for v in suzuki_variants)
    is_cruiser = any(v in q for v in cruiser_variants)

    # 2. Context Extraction (Fallback if no explicit car keyword is matched)
    last_mentioned_car = None
    if "messages" in st.session_state:
        for msg in reversed(st.session_state.messages[-4:]):
            if "content" in msg:
                content = msg["content"].lower()
                if any(v in content for v in corolla_variants):
                    last_mentioned_car = "corolla"
                    break
                elif any(v in content for v in civic_variants):
                    last_mentioned_car = "civic"
                    break
                elif any(v in content for v in suzuki_variants):
                    last_mentioned_car = "suzuki"
                    break
                elif any(v in content for v in cruiser_variants):
                    last_mentioned_car = "land_cruiser"
                    break

    # 3. Identity Check
    if "who are you" in q or "introduce yourself" in q:
        return {
            "type": "text",
            "response": "Hi 👋\n\nI am Sara from customer support department.\n\nFor further queries contact our manager:\nAli Huzaifa."
        }
    
    # 4. Context-Driven Brand Filters (Prioritizes current explicit typing over old session states)
    # UPDATED: Evaluates both c["brand"] and c["name"] fields to correctly match text entries
    if (is_corolla or (last_mentioned_car == "corolla" and not (is_civic or is_suzuki or is_cruiser))) and has_image_keyword:
        corollas = [p for p, c in car_database.items() if "corolla" in c["brand"].lower() or "corolla" in c["name"].lower()]
        return {"type": "car_list", "cars": corollas, "brand_label": "Corolla"}

    if (is_civic or (last_mentioned_car == "civic" and not (is_corolla or is_suzuki or is_cruiser))) and has_image_keyword:
        civics = [p for p, c in car_database.items() if "civic" in c["brand"].lower() or "civic" in c["name"].lower()]
        return {"type": "car_list", "cars": civics, "brand_label": "Honda Civic"}

    if (is_suzuki or (last_mentioned_car == "suzuki" and not (is_corolla or is_civic or is_cruiser))) and has_image_keyword:
        suzukis = [p for p, c in car_database.items() if "suzuki" in c["brand"].lower() or "suzuki" in c["name"].lower()]
        return {"type": "car_list", "cars": suzukis, "brand_label": "Suzuki"}

    if (is_cruiser or (last_mentioned_car == "land_cruiser" and not (is_corolla or is_civic or is_suzuki))) and has_image_keyword:
        cruisers = [p for p, c in car_database.items() if "cruiser" in c["brand"].lower() or "cruiser" in c["name"].lower() or "land" in c["name"].lower()]
        return {"type": "car_list", "cars": cruisers, "brand_label": "Toyota Land Cruiser"}

    # 5. Fixed Direct License Plate Matching Pattern
    for plate in car_database.keys():
        clean_plate = plate.replace("-", "").upper()
        if clean_plate in clean_query.upper():
            return {
                "type": "car_detail",
                "plate": plate
            }

    # 6. Appointment Route
    buy_words = ["buy", "purchase", "book", "meeting", "appointment", "test drive", "schedule", "register", "reserve", "reservation"]
    if any(word in q for word in buy_words):
        return {
            "type": "appointment"
        }

    return None

# ---------------- SESSION MANAGEMENT ----------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hey 👋 Welcome to CarWala Pakistan. Ask me about any car."
        }
    ]

if "booking_state" not in st.session_state:
    st.session_state.booking_state = {
        "is_active": False,
        "step": None,
        "name": None,
        "contact": None
    }

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("CarWala AI Workspace")
    if st.button("Clear Chat Window"):
        st.session_state.messages = [{"role": "assistant", "content": "Welcome back 🚗"}]
        st.session_state.booking_state = {"is_active": False, "step": None, "name": None, "contact": None}
        st.rerun()

# ---------------- CHAT HISTORY RENDERING ----------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "global_car_list":
            st.write("### 🚗 Complete Showroom Stock Inventory")
            cols = st.columns(2)
            for idx, plate in enumerate(msg["cars"]):
                with cols[idx % 2]:
                    car = car_database[plate]
                    if os.path.exists(car["image"]):
                        st.image(car["image"], use_container_width=True)
                    else:
                        st.warning(f"⚠️ Image asset missing for: {plate}")
                    st.write(f"**{car['name']}**\n* 💰 Price: {car['price']}\n* 🔤 Plate: `{plate}`")
            st.info(msg["content"])
            
        elif msg.get("type") == "car_list":
            st.write(f"### 🎯 Available {msg.get('brand_label', 'Matching')} Collection")
            cols = st.columns(2)
            for idx, plate in enumerate(msg["cars"]):
                with cols[idx % 2]:
                    car = car_database[plate]
                    if os.path.exists(car["image"]):
                        st.image(car["image"], use_container_width=True)
                    else:
                        st.warning(f"⚠️ Display thumbnail unreadable for: {plate}")
                    st.write(f"**{car['name']}**\n* 💰 Price: {car['price']}\n* 🔤 Plate: `{plate}`")
            st.info(msg["content"])
            
        elif msg.get("type") == "car_detail":
            if os.path.exists(msg["image"]):
                st.image(msg["image"], width=450)
            else:
                st.error("⚠️ Detailed profile layout image could not be loaded from local files.")
            st.write(msg["content"])
            
        else:
            st.write(msg["content"])

# ---------------- EVALUATION RUNTIME LOOP ----------------

user_query = st.chat_input("Ask about Corolla, Civic, prices...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    if st.session_state.booking_state["is_active"]:
        current_step = st.session_state.booking_state["step"]

        if current_step == "get_name":
            st.session_state.booking_state["name"] = user_query
            st.session_state.booking_state["step"] = "get_contact"
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Thank you! Now, please enter your **Contact Number** to finalize the request:"
            })

        elif current_step == "get_contact":
            st.session_state.booking_state["contact"] = user_query
            cust_name = st.session_state.booking_state["name"]
            cust_phone = st.session_state.booking_state["contact"]
            
            st.session_state.booking_state = {"is_active": False, "step": None, "name": None, "contact": None}

            confirmation = f"""
### 🎉 Reservation Registered Successfully!

**Customer Dossier Summary:**
* 👤 **Name:** {cust_name}
* 📞 **Contact Number:** {cust_phone}

Our manager **Ali Huzaifa** will call you shortly to lock in your priority showroom meeting time slot. Thank you for choosing CarWala Pakistan!
"""
            st.session_state.messages.append({"role": "assistant", "content": confirmation})

    else:
        special = handle_special_cases(user_query)

        if special:
            if special["type"] == "text":
                st.session_state.messages.append({"role": "assistant", "content": special["response"]})

            elif special["type"] == "global_car_list":
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "global_car_list",
                    "cars": special["cars"],
                    "content": "Type any specific plate number shown above to view detailed engine options and pricing structure!"
                })

            elif special["type"] == "car_list":
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "car_list",
                    "cars": special["cars"],
                    "brand_label": special["brand_label"],
                    "content": f"We found these matching {special['brand_label']} profiles! Reply with your target plate number to load specifics or register a booking."
                })

            elif special["type"] == "car_detail":
                plate = special["plate"]
                car = car_database[plate]
                specs = f"### 📊 Vehicle Dossier: {car['name']}\n\n* **Brand:** {car['brand']}\n* **Showroom Valuation:** `{car['price']}`\n* **Current Mileage:** {car['mileage']}\n* **Powertrain Fuel Type:** {car['fuel']}\n* **Registration Tag:** `{plate}`"
                st.session_state.messages.append({
                    "role": "assistant",
                    "type": "car_detail",
                    "image": car["image"],
                    "content": specs
                })

            elif special["type"] == "appointment":
                st.session_state.booking_state["is_active"] = True
                st.session_state.booking_state["step"] = "get_name"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Let's setup your showroom booking entry! Please enter your **Full Name** to start:"
                })
                
        else:
            answer = generate_car_response(user_query)
            st.session_state.messages.append({"role": "assistant", "content": answer})

    st.rerun()