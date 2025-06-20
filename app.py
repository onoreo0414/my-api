{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "bd3eab48",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Requirement already satisfied: flask in c:\\users\\onoreo\\anaconda3\\lib\\site-packages (1.1.2)\n",
      "Collecting flask_httpauth\n",
      "  Downloading Flask_HTTPAuth-4.8.0-py3-none-any.whl (7.0 kB)\n",
      "Requirement already satisfied: itsdangerous>=0.24 in c:\\users\\onoreo\\anaconda3\\lib\\site-packages (from flask) (2.0.1)\n",
      "Requirement already satisfied: Jinja2>=2.10.1 in c:\\users\\onoreo\\anaconda3\\lib\\site-packages (from flask) (2.11.3)\n",
      "Requirement already satisfied: Werkzeug>=0.15 in c:\\users\\onoreo\\anaconda3\\lib\\site-packages (from flask) (2.0.3)\n",
      "Requirement already satisfied: click>=5.1 in c:\\users\\onoreo\\anaconda3\\lib\\site-packages (from flask) (8.0.4)\n",
      "Requirement already satisfied: colorama in c:\\users\\onoreo\\anaconda3\\lib\\site-packages (from click>=5.1->flask) (0.4.5)\n",
      "Requirement already satisfied: MarkupSafe>=0.23 in c:\\users\\onoreo\\anaconda3\\lib\\site-packages (from Jinja2>=2.10.1->flask) (2.0.1)\n",
      "Installing collected packages: flask_httpauth\n",
      "Successfully installed flask_httpauth-4.8.0\n"
     ]
    }
   ],
   "source": [
    "!pip install flask flask_httpauth"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "5bf8b312",
   "metadata": {},
   "outputs": [],
   "source": [
    "from flask import Flask, request, jsonify\n",
    "from flask_httpauth import HTTPBasicAuth\n",
    "from werkzeug.security import generate_password_hash, check_password_hash\n",
    "import re\n",
    "\n",
    "app = Flask(__name__)\n",
    "auth = HTTPBasicAuth()\n",
    "\n",
    "# ユーザー情報の保存（簡易DB）\n",
    "users_db = {}\n",
    "\n",
    "# テスト用アカウント\n",
    "users_db[\"TaroYamada\"] = {\n",
    "    \"password\": generate_password_hash(\"OnoReo20010414\"),\n",
    "    \"nickname\": \"Ono Reo\",\n",
    "    \"comment\": \"Hello!\"\n",
    "}\n",
    "\n",
    "# Base64認証用\n",
    "@auth.verify_password\n",
    "def verify_password(username, password):\n",
    "    if username in users_db and check_password_hash(users_db[username][\"password\"], password):\n",
    "        return username\n",
    "    return None\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "8bfc8a03",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route('/signup', methods=['POST'])\n",
    "def signup():\n",
    "    data = request.json\n",
    "    user_id = data.get('user_id')\n",
    "    password = data.get('password')\n",
    "\n",
    "    # バリデーション\n",
    "    if not user_id or not password:\n",
    "        return jsonify(message=\"Account creation failed\", cause=\"Required user_id and password\"), 400\n",
    "    if not re.fullmatch(r'[A-Za-z0-9]{6,20}', user_id):\n",
    "        return jsonify(message=\"Account creation failed\", cause=\"Incorrect character pattern\"), 400\n",
    "    if not re.fullmatch(r'[\\x21-\\x7E]{8,20}', password):\n",
    "        return jsonify(message=\"Account creation failed\", cause=\"Incorrect character pattern\"), 400\n",
    "    if user_id in users_db:\n",
    "        return jsonify(message=\"Account creation failed\", cause=\"Already same user_id is used\"), 400\n",
    "\n",
    "    users_db[user_id] = {\n",
    "        \"password\": generate_password_hash(password),\n",
    "        \"nickname\": user_id,\n",
    "        \"comment\": \"\"\n",
    "    }\n",
    "\n",
    "    return jsonify(message=\"Account successfully created\", user={\"user_id\": user_id, \"nickname\": user_id}), 200\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "0330c0c8",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route('/users/<user_id>', methods=['GET'])\n",
    "@auth.login_required\n",
    "def get_user(user_id):\n",
    "    current_user = auth.current_user()\n",
    "    if user_id not in users_db:\n",
    "        return jsonify(message=\"No user found\"), 404\n",
    "    if current_user != user_id:\n",
    "        return jsonify(message=\"Authentication failed\"), 401\n",
    "\n",
    "    user = users_db[user_id]\n",
    "    nickname = user.get(\"nickname\", user_id)\n",
    "    comment = user.get(\"comment\", \"\")\n",
    "    return jsonify(message=\"User details by user_id\", user={\n",
    "        \"user_id\": user_id,\n",
    "        \"nickname\": nickname or user_id,\n",
    "        \"comment\": comment\n",
    "    }), 200\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "0e56419b",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route('/users/<user_id>', methods=['PATCH'])\n",
    "@auth.login_required\n",
    "def update_user(user_id):\n",
    "    current_user = auth.current_user()\n",
    "    if current_user != user_id:\n",
    "        return jsonify(message=\"No permission, for update\"), 403\n",
    "    if user_id not in users_db:\n",
    "        return jsonify(message=\"No user found\"), 404\n",
    "\n",
    "    data = request.json or {}\n",
    "    nickname = data.get(\"nickname\")\n",
    "    comment = data.get(\"comment\")\n",
    "\n",
    "    if nickname is None and comment is None:\n",
    "        return jsonify(message=\"User updation failed\", cause=\"Required nickname or comment\"), 400\n",
    "\n",
    "    if nickname is not None:\n",
    "        if len(nickname) > 30:\n",
    "            return jsonify(message=\"User updation failed\", cause=\"Invalid nickname or comment\"), 400\n",
    "        users_db[user_id][\"nickname\"] = nickname or user_id\n",
    "\n",
    "    if comment is not None:\n",
    "        if len(comment) > 100:\n",
    "            return jsonify(message=\"User updation failed\", cause=\"Invalid nickname or comment\"), 400\n",
    "        users_db[user_id][\"comment\"] = comment or \"\"\n",
    "\n",
    "    return jsonify(message=\"User successfully updated\", user={\n",
    "        \"user_id\": user_id,\n",
    "        \"nickname\": users_db[user_id][\"nickname\"],\n",
    "        \"comment\": users_db[user_id][\"comment\"]\n",
    "    }), 200\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "944493f7",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route('/close', methods=['POST'])\n",
    "@auth.login_required\n",
    "def close_account():\n",
    "    current_user = auth.current_user()\n",
    "    if current_user not in users_db:\n",
    "        return jsonify(message=\"No user found\"), 404\n",
    "    del users_db[current_user]\n",
    "    return jsonify(message=\"Account and user successfully removed\"), 200\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "c9cfc1b9",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app \"__main__\" (lazy loading)\n",
      " * Environment: production\n",
      "\u001b[31m   WARNING: This is a development server. Do not use it in a production deployment.\u001b[0m\n",
      "\u001b[2m   Use a production WSGI server instead.\u001b[0m\n",
      " * Debug mode: off\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " * Running on all addresses.\n",
      "   WARNING: This is a development server. Do not use it in a production deployment.\n",
      " * Running on http://192.168.1.23:5000/ (Press CTRL+C to quit)\n"
     ]
    }
   ],
   "source": [
    "from threading import Thread\n",
    "\n",
    "def run_app():\n",
    "    app.run(host='0.0.0.0', port=5000)\n",
    "\n",
    "Thread(target=run_app).start()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "85270fb8",
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route('/')\n",
    "def home():\n",
    "    return \"Hello from Render!\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "cf6678ec",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.13"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
