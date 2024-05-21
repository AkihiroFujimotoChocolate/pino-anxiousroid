# pino-anxiousroid
## Example of Environment Variables for Local Execution
Create a .env file in app directory as follows
```shell
AI_NOVELIST_API_KEY = your_ai_novelist_api_key
AI_NOVELIST_API_SERVER_URL = ai_novelist_api_server_url
```

## How to Run on Windows
1. Create a python v3.11 virtual environment in your project directory
```powershell
python3.11 -m venv .venv
```
2. Activate the virtual environment
```powershell
.\.venv\Scripts\Activate.ps1
```
3. While the virtual environment is active, install the required packages
```powershell
pip install -r requirements.txt
```
4. Run the FastAPI App
```powershell
streamlit run ./app/main.py
```

## How to Run on Linux
1. Create a python v3.11 virtual environment in your project directory
```shell
python3.11 -m venv .venv
```
2. Activate the virtual environment
```shell
source .venv/bin/activate
```
3. While the virtual environment is active, install the required packages
```shell
pip install -r requirements.txt
```
4. Run the FastAPI App
```shell
streamlit run ./app/main.py
```
