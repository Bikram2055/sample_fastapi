from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from typing import List
import os
from datetime import datetime
import json
import environ

# Initialize the environment
env = environ.Env()
environ.Env.read_env()

app = FastAPI()

# Load the competition times from the environment
COMPETITION_START_TIME = datetime.strptime(env('COMPETITION_START_TIME'), '%Y-%m-%d %H:%M:%S')
COMPETITION_END_TIME = datetime.strptime(env('COMPETITION_END_TIME'), '%Y-%m-%d %H:%M:%S')


# Base directory to save uploaded files
UPLOAD_DIRECTORY = "uploaded_files"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_form():
    current_time = datetime.now()
    if current_time < COMPETITION_START_TIME:
        # Before the competition
        return HTMLResponse(content=open("to_start.html").read())
    elif COMPETITION_START_TIME <= current_time <= COMPETITION_END_TIME:
        # During the competition
        return HTMLResponse(content=open("forms.html").read())
    else:
        # After the competition
        return HTMLResponse(content=open("time_over.html").read())

@app.post("/success")
async def handle_form(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    discord: str = Form(...),
    project_file: UploadFile = File(...),
    build_file: UploadFile = File(...)
):
    email_key = email.split('@')[0]

    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

    folder_name = f"{email_key}_{current_time}"
    folder_path = os.path.join(UPLOAD_DIRECTORY, folder_name)

    os.makedirs(folder_path, exist_ok=True)

    files = [project_file, build_file]
    file_dict = {folder_name: []}

    for file in files:
        file_path = os.path.join(folder_path, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            file_dict[folder_name].append({
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            })

    user_details = {
        "name": name,
        "email": email,
        "phone": phone,
        "discord": discord,
        "submission_time": current_time,
    }

     # Save the user details in a JSON file inside the created folder
    json_file_path = os.path.join(folder_path, "user_details.json")
    with open(json_file_path, "w") as json_file:
        json.dump(user_details, json_file, indent=4)

    # HTML response with a thank-you message
    thank_you_html = f"""
    <html>
        <head>
            <title>Thank You!</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
                .thank-you-card {{
                    background-color: #fff;
                    padding: 20px 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    text-align: center;
                    width: 400px;
                }}
                .thank-you-card h2 {{
                    color: #4CAF50;
                    margin-bottom: 10px;
                }}
                .thank-you-card p {{
                    color: #333;
                    margin-bottom: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="thank-you-card">
                <h2>Thank You, {name}!</h2>
                <p>Your files have been successfully uploaded.</p>
                <p>Submission Time: {current_time}</p>
            </div>
        </body>
    </html>
    """
    
    return HTMLResponse(content=thank_you_html)

@app.get("/start-time")
async def get_current_datetime():

    formatted_datetime = COMPETITION_START_TIME.strftime("%b %d, %Y %H:%M:%S")

    # Return the current date and time as a JSON response
    return {
        "start_time": formatted_datetime
    }