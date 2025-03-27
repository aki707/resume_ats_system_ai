# Resume ATS System AI

## Setup Instructions

### 1. Create Virtual Environment
```sh
python -m venv .venv
```

#### Activate Virtual Environment
- **Windows**:
  ```sh
  .venv\Scripts\activate
  ```
- **Mac/Linux**:
  ```sh
  source .venv/bin/activate
  ```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Set Environment Variables
Copy `.env.sample` to `.env` and update values as needed:
```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GROQ_API_KEY=your_groq_api_key_here
```
- u can have groq api key from here : [https://console.groq.com/keys]


### 4. Run Database Migrations
```sh
python backend/manage.py makemigrations
python backend/manage.py migrate
```

### 5. Start the Django Server
```sh
python backend/manage.py runserver
```
- Access the backend at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 6. Start the Streamlit App
```sh
streamlit run frontend/app.py
```