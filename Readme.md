# 🚗 CarWala Pakistan - AI Car Retail Assistant

An intelligent AI-powered showroom assistant built using **Streamlit**, **Groq LLM**, and a structured vehicle inventory database.

The chatbot simulates a real car dealership experience by helping customers:

* Search available vehicles
* View car details
* Retrieve vehicle images
* Check prices and mileage
* Ask inventory-related questions
* Schedule appointments and test drives
* Interact naturally with an AI showroom representative

---

## 🌟 Features

### 🤖 AI-Powered Showroom Assistant

The assistant uses **Llama 3.1 8B Instant** via Groq to provide natural and conversational responses.

### 🚘 Live Inventory Search

Users can ask questions such as:

* Do you have a Corolla?
* Show Honda Civic pictures
* What is the price of BFB-892?
* Tell me about Land Cruiser inventory

The assistant searches the inventory database and returns relevant information.

### 🖼 Vehicle Image Retrieval

The chatbot can display images of vehicles directly from inventory records.

Example:

```text
Show me Corolla images
```

### 🔍 License Plate Lookup

Supports direct vehicle retrieval using registration numbers.

Example:

```text
Tell me about CY-9081
```

### 🧠 Context-Aware Conversations

The assistant remembers recent conversation context and understands follow-up questions.

Example:

```text
User: Show Corolla images
User: What is the price of the first one?
```

### 📅 Appointment & Test Drive Requests

Users can request:

* Vehicle reservations
* Test drives
* Purchase appointments

### 🚫 Out-of-Stock Detection

If a customer asks about a vehicle not available in inventory, the assistant politely informs them.

Example:

```text
Do you have a Prius?
```

---

## 🏗 Architecture

```text
┌────────────────────┐
│     Streamlit UI    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Business Logic      │
│ Routing Engine      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Vehicle Database    │
│ cars.json           │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Groq LLM API        │
│ Llama 3.1 8B        │
└────────────────────┘
<img src=""E:\car-retailer-chatbot\Car Retail Chatbot\Architecture.png"" width="900">

```

---

## 🛠 Tech Stack

| Technology           | Purpose           |
| -------------------- | ----------------- |
| Streamlit            | Frontend UI       |
| Python               | Backend Logic     |
| Groq API             | LLM Inference     |
| Llama 3.1 8B Instant | Conversational AI |
| JSON Database        | Vehicle Inventory |
| GitHub               | Version Control   |

---

## 📂 Project Structure

```text
Car Retail Chatbot/
│
├── app.py
├── cars.json
├── carinventory.docx
├── requirements.txt
│
├── images/
│   ├── car_honda_civic_CY9081.png
│   ├── car_toyota_corolla_BFB892.png
│   ├── car_toyota_corolla_AKW415.png
│   └── ...
│
└── .streamlit/
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/alihuzaifa2004/Car-Retail-Chatbot.git
cd Car-Retail-Chatbot
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure API Key

Create environment variable:

```env
GROQ_API_KEY=YOUR_API_KEY
```

Or configure Streamlit secrets:

```toml
GROQ_API_KEY="YOUR_API_KEY"
```

### Run Application

```bash
streamlit run app.py
```

---

## 💬 Example Queries

```text
Show Corolla images

Do you have Honda Civic available?

Tell me about CY-9081

Show all available cars

I want to book a test drive

What Toyota vehicles are available?
```

---

## 📊 Current Inventory Categories

### Toyota

* Corolla Altis X Grande
* Corolla GLI
* Land Cruiser V8
* Land Cruiser ZX Modellista

### Honda

* Civic Oriel Turbo

### Suzuki

* Bolan VX
* Bolan VXR
* Every GA
* Every Join Turbo

---

## 🔮 Future Improvements

* RAG-based knowledge retrieval
* ChromaDB vector database
* PDF & DOCX ingestion
* Vehicle comparison engine
* Voice assistant support
* Customer lead management
* Multi-language support
* Real-time inventory synchronization
* WhatsApp integration

---

## 🌐 Deployment

The project can be deployed using:

### Streamlit Community Cloud

https://streamlit.io/cloud

### Local Deployment

```bash
streamlit run app.py
```

---

## 👨‍💻 Author

### Ali Huzaifa

LinkedIn:

[www.linkedin.com/in/ali-huzaifa-5381b8202](http://www.linkedin.com/in/ali-huzaifa-5381b8202)

GitHub:

https://github.com/alihuzaifa2004

---

## ⭐ Support

If you found this project useful:

* Star the repository
* Fork the project
* Share feedback
* Contribute enhancements

---

Built with ❤️ using Streamlit, Groq, and Llama 3.1.
