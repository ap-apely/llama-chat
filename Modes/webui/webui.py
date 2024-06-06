from flask import Flask, render_template, request, jsonify, Response
import requests
import json

app = Flask(__name__)

# Base URL of your API
API_BASE_URL = "http://localhost:8000"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/create-user', methods=['POST'])
def create_user():
    user_data = request.json
    print(user_data)
    response = requests.post(f"{API_BASE_URL}/users/", json=user_data)
    print(response.status_code)
    if response.status_code == 200:
        print("Sucess")
        data = {
            "Request" : "Sucess"
        }
        print(jsonify(data).json)
        return Response("{'a':'b'}", status=200, mimetype='application/json')
    elif response.status_code == 400:
        print("User already exist")
        data = {
            "Request" : "Useralreadyexist"
        }
        print(jsonify(data).json)
        return Response("{'a':'b'}", status=400, mimetype='application/json')
    else:
        return jsonify("Undefined error")

@app.route('/api/token', methods=['POST'])
def token():
    user_data = request.json
    response = requests.post(f"{API_BASE_URL}/token/", data=user_data)
    print("token")
    print(json.loads(response.text))
    return json.loads(response.text)

@app.route('/api/create-conversation', methods=['POST'])
def create_conversation():
    token = request.headers.get("Authorization").split(" ")[1]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE_URL}/create-conversation", headers=headers)
    print(response.json)
    return jsonify(response.json())

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data['user_input']
    conversation_id = data.get('conversation_id')
    token = request.headers.get("Authorization").split(" ")[1]
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        'message': user_input,
        'conversation_id': conversation_id
    }
    response = requests.post(f"{API_BASE_URL}/chat", params=params, headers=headers)
    text_response = response.json().get("response")
    return text_response["content"]

if __name__ == '__main__':
    app.run(debug=True)
