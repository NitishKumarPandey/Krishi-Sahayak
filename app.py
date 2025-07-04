from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import requests
from gtts import gTTS
import string
import random
import base64

load_dotenv()
groq_api_key = os.getenv('groq_api_key')


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'webm', 'wav', 'mp3'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/audio', exist_ok=True)

# Set the secret key for session management
app.secret_key = 'your secret key'


def get_answer_groq(question):
    # Groq API endpoint for chat completions
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3-8b-8192",  # Use appropriate Groq model
        "messages": [
            {"role": "system", "content": "I want you to act like a helpful agriculture chatbot and help farmers with their query"},
            {"role": "user", "content": "Give a Brief Of Agriculture Seasons in India"},
            {"role": "system", "content": "In India, the agricultural season consists of three major seasons: the Kharif (monsoon), the Rabi (winter), and the Zaid (summer) seasons. Each season has its own specific crops and farming practices.\n\n1. Kharif Season (Monsoon Season):\nThe Kharif season typically starts in June and lasts until September. This season is characterized by the onset of the monsoon rains, which are crucial for agricultural activities in several parts of the country. Major crops grown during this season include rice, maize, jowar (sorghum), bajra (pearl millet), cotton, groundnut, turmeric, and sugarcane. These crops thrive in the rainy conditions and are often referred to as rain-fed crops.\n\n2. Rabi Season (Winter Season):\nThe Rabi season usually spans from October to March. This season is characterized by cooler temperatures and lesser or no rainfall. Crops grown during the Rabi season are generally sown in October and harvested in March-April. The major Rabi crops include wheat, barley, mustard, peas, gram (chickpeas), linseed, and coriander. These crops rely mostly on irrigation and are well-suited for the drier winter conditions.\n\n3. Zaid Season (Summer Season):\nThe Zaid season occurs between March and June and is a transitional period between Rabi and Kharif seasons. This season is marked by warmer temperatures and relatively less rainfall. The Zaid crops are grown during this time and include vegetables like cucumber, watermelon, muskmelon, bottle gourd, bitter gourd, and leafy greens such as spinach and amaranth. These crops are generally irrigated and have a shorter growing period compared to Kharif and Rabi crops.\n\nThese three agricultural seasons play a significant role in India's agricultural economy and provide stability to food production throughout the year. Farmers adapt their farming practices and crop selection accordingly to make the best use of the prevailing climatic conditions in each season."},
            {"role": "user", "content": question}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"

def speech_to_text_groq(audio_file_path):
    # Convert audio to base64 for sending to Groq API
    with open(audio_file_path, "rb") as audio_file:
        audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
    
    # Groq API endpoint for audio transcription
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {groq_api_key}"
    }
    
    # Prepare multipart form data
    files = {
        'file': (os.path.basename(audio_file_path), open(audio_file_path, 'rb'), 'audio/webm'),
    }
    
    data = {
        'model': 'whisper-large-v3'  # Use appropriate transcription model
    }
    
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        return response.json().get('text', '')
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return "Sorry, there was an error transcribing your audio."

def text_to_audio(text, filename):
    tts = gTTS(text)
    tts.save(f'static/audio/{filename}.mp3')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/chat-response', methods=['POST'])
def chat_response():
    if 'audio' in request.files:
        audio = request.files['audio']
        if audio and allowed_file(audio.filename):
            filename = secure_filename(audio.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio.save(filepath)
            transcription = speech_to_text_groq(filepath)
            return jsonify({'text': transcription})

    text = request.form.get('text')
    if text:
        response = process_text(text)
        return {'text': response['text'], 'voice': url_for('static', filename='audio/' + response['voice'])}

    return jsonify({'text': 'Invalid request'})

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_text(text):
    # Process text input using Groq API
    return_text = get_answer_groq(text)
    # Generate random string for audio filename
    res = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    text_to_audio(return_text, res)
    return {"text": return_text, "voice": f"{res}.mp3"}


# Database connection function
def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            port=3308,
            database='farm1_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"Database Connection Error: {e}")
        return None

@app.route('/login', methods=['GET', 'POST']) 
def login(): 
    msg = '' 
    if request.method == 'POST':
        # getting id and password
        username = request.form['username'] 
        password = request.form['password'] 
        
        # Establish database connection
        connection = get_db_connection()
        
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)
        
        try:
            with connection.cursor() as cursor:
                # getting farmer where id and password matches
                cursor.execute('SELECT * FROM farmer WHERE username = %s AND Password = %s', (username, password))
                account = cursor.fetchone()

                if account:
                    # if account found then log in successful
                    session['loggedin'] = True
                    session['id'] = account['id'] 
                    msg = 'Logged in successfully!!!'   
                
                    if account['F_Firstname'] == '' and account['F_Lastname'] == '':
                        # if firstname and lastname is none or empty and then complete profile
                        msg = "complete your profile"
                        return render_template("complete.html")
                    
                    # getting farmer info where id and password matches
                    cursor.execute('SELECT * FROM farmer WHERE id = %s', (session['id'],)) 
                    info = cursor.fetchone()
                    data = {'user_id': session['id'], 'msg': msg, 'info': info}

                    # displaying farmer basic info 
                    return redirect(url_for('home'))
                else:
                    # if username/password not matching with our database or not present in database then displaying error 
                    msg = 'Incorrect username / password!!!'
        
        except Exception as e:
            print(f"Login Error: {e}")
            msg = 'An error occurred during login'
        
        finally:
            connection.close()
    
    return render_template('login.html', msg=msg)
@app.route('/')

# logout route
@app.route('/logout') 
def logout():
    
    # removing data of current logged in farmer from sessions  
    session.pop('loggedin', None) 
    session.pop('id', None) 
    session.pop('username', None) 
    return redirect(url_for('login')) 

# signup route
@app.route('/signup', methods =['GET', 'POST']) 
def signup(): 
    msg = ''
    if request.method == 'POST':
        # getting new id and new password
        username = request.form['username'] 
        password = request.form['password']
        print(username, password)
        
        # Establish database connection
        connection = get_db_connection()
        
        if connection is None:
            msg = 'Database connection failed'
            return render_template('signup.html', msg=msg)
        
        try:
            with connection.cursor() as cursor:
                # check if user already exists
                cursor.execute('SELECT * FROM farmer WHERE username = %s', (username )) 
                account = cursor.fetchone() 
                
                if account:
                    # if user already exists then displaying error
                    msg = 'Account already exists!!!'
                else: 
                    # if user doesn't exist then create new user
                    cursor.execute('INSERT INTO farmer (F_Firstname, F_Lastname, F_Email, F_Phone, F_Income, username, Password) VALUES ("", "", "", "", 0, %s, %s)', (username, password)) 
                    connection.commit() 
                    msg = 'You have successfully registered!!!'
                    return render_template('login.html', msg=msg)   

        except Exception as e:
            print(f"Signup Error: {e}")
            msg = 'An error occurred during signup'
        
        finally:
            connection.close()
    
    return render_template('signup.html', msg=msg)# complete route

@app.route('/complete', methods=['GET', 'POST'])
def complete():
    msg = "Please first create user!!!"
    data = {'user_id': None, 'msg': msg, 'info': None}  # Default initialization
    
    if request.method == 'POST':
        # Retrieve form data
        first = request.form.get('first', '').strip()
        last = request.form.get('last', '').strip()
        gender = request.form.get('gender', '').strip()
        address = request.form.get('address', '').strip()
        contact = request.form.get('contact', '').strip()

        # Check if user is logged in
        if 'id' not in session:
            msg = 'Please log in first'
            return render_template('login.html', msg=msg)

        user_id = session['id']
        connection = get_db_connection()

        if connection is None:
            msg = 'Database connection failed'
            return render_template('complete.html', msg=msg)

        try:
            with connection.cursor() as cursor:
                # Update user profile
                cursor.execute(
                    'UPDATE farmer SET F_Firstname=%s, F_Lastname=%s, F_Gender=%s, F_Address=%s, F_ContactNo=%s WHERE id=%s',
                    (first, last, gender, address, contact, user_id)
                )
                connection.commit()

                # Fetch updated user info
                cursor.execute('SELECT * FROM farmer WHERE id = %s', (user_id,))
                info = cursor.fetchone()

                msg = "Successfully completed profile!!!"
                data = {
                    'user_id': user_id,
                    'msg': msg,
                    'info': info
                }
        except Exception as e:
            print(f"Complete Error: {e}")
            msg = 'An error occurred during profile completion'
            data['msg'] = msg
        finally:
            if connection:
                connection.close()
    
    return render_template('index.html', **data)


def getProfitLoss():
    msg=''

    total_sp = 0
    exp1 = 0
    exp2 = 0
    exp3 = 0

    # getting selling prices of every crop and all expences and calculating its sum
    sql1 = "SELECT Selling_price FROM crop_market WHERE User_id = '" +  str(session['id'] ) + "'"
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('login.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute(sql1)
            total_sp = cursor.fetchall()
            total_sp = calculate_total(total_sp)

        except Exception as e:
            print(f"Profit Loss Error: {e}")

    
    q1 = "SELECT seed_price FROM seed WHERE User_id = '" + str(session['id']) + "'"
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('login.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute(q1)
            exp1 = cursor.fetchall()
            exp1 = calculate_total(exp1)
        except Exception as e:
            print(f"Profit Loss Error: {e}")
    
    q2 = "SELECT pesticide_price FROM pesticide WHERE User_id = '" + str(session['id']) + "'"
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('login.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute(q2)
            exp2 = cursor.fetchall()
            exp2 = calculate_total(exp2)
        except Exception as e:
            print(f"Profit Loss Error: {e}")

    q3 = "SELECT fertilizer_price FROM fertilizer WHERE User_id = '" + str(session['id']) + "'"
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('login.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute(q3)
            exp3 = cursor.fetchall()
            exp3 = calculate_total(exp3)
        except Exception as e:
            print(f"Profit Loss Error: {e}")

    q4 = "SELECT salary FROM labour WHERE User_id = '" + str(session['id']) + "'"
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('login.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute(q4)
            exp4 = cursor.fetchall()
            exp4 = calculate_total(exp4)
        except Exception as e:
            print(f"Profit Loss Error: {e}")

    total_exp = exp1 + exp2 + exp3 + exp4
    values = [exp1, exp2, exp3, exp4]
    data = {'user_id': session['id'], 'msg': msg, 'values': values, 'total_exp': total_exp, 'sp': total_sp, 'color': 'primary'}

    if (total_sp - total_exp) > 0:
        data['color'] = '#2e7d32'
    elif (total_sp - total_exp) < 0:
        data['color'] = '#d32f2f'
    
    print(data)
        
    return data


# from now 9 routes are used for displaying respected data and if no data found then display error
# 1 - home route - to main user page
@app.route('/home')
def home():
    datas = getProfitLoss()
    api_key = os.getenv("API_KEY")
    sell = {
                'profit': datas['sp'] - datas['total_exp'],
                'expenditure': datas['total_exp'],
                'color' : datas['color'],
                "api_key" : api_key
            }
    data = {'info': sell}
    # print(data)
    try:
        article_data = requests.get("https://gnews.io/api/v4/search?q=agriculture&lang=en&country=in&max=10&apikey=" + api_key).json()
        # print(article_data)
        data['articles'] = article_data['articles']
    except Exception as e:
        print(f"Article Error: {e}")
    print(data)

    return render_template('index.html', **data)
        


# 2 - farm route - to display farm data
@app.route('/farm')
def farm():
    msg = ""
    if 'id' not in session:
        msg = "User not logged in!"
        return render_template('index.html', msg=msg)

    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)

    try:
        with connection.cursor() as cursor:
            # Fetch farm data for the logged-in user
            cursor.execute('SELECT * FROM farm WHERE User_id = %s', (session['id'],))
            info = cursor.fetchall()
            if not info:
                msg = "Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            print(data)
        return render_template('farm.html', info=info, msg=msg)
    except Exception as e:
        print(f"Farm Error: {e}")
        msg = "An error occurred while fetching farm data."
        return render_template('farm.html', info=[], msg=msg)
    finally:
        connection.close()
# 3 - crop_allocation route - to display all currently allocated crop data
@app.route('/crop_allocation')
def crop_allocation():
    msg=""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM crop_allocation WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            print(data)
            return render_template('crop_allocation.html', **data)

        except Exception as e:
            print(f"Crop Allocation Error: {e}")   
            msg = 'An error occurred during crop allocation'

# 4 - seed route - to display all seeds data 
@app.route('/seed')
def seed():
    msg=""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM seed WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            # for d in info:
            #     _ = d.popitem()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('seed.html', **data)

        except Exception as e:
            print(f"Seed Error: {e}")   
            msg = 'An error occurred during seed'
    

# 5 - pesticide route - to display all pesticides data
@app.route('/pesticide')
def pesticide():
    msg=""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM pesticide WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            # for d in info:
            #     _ = d.popitem()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('pesticide.html', **data)

        except Exception as e:
            print(f"Pesticide Error: {e}")   
            msg = 'An error occurred during pesticide'

# 6 - fertilizers route - to display all fertilizers data
@app.route('/fertilizer')
def fertilizer():
    msg=""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM fertilizer WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            # for d in info:
            #     _ = d.popitem()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('fertilizer.html', **data)

        except Exception as e:
            print(f"Fertilizer Error: {e}")   
            msg = 'An error occurred during fertilizer'

# 7 - labour route - to display all labours data
@app.route('/labour')
def labour():
    msg=""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM labour WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            print(data)
            return render_template('labour.html', info=info, msg=msg)

    except Exception as e:
        print(f"Labour Error: {e}")   
        msg = 'An error occurred during labour'

# 8 - warehouse route - to display all warehouses data where crops are stored
@app.route('/warehouse')
def warehouse():
    msg=""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM warehouse WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('warehouse.html', info=info, msg=msg)

        except Exception as e:
            print(f"warehouse Error: {e}")   
            msg = 'An error occurred during warehouse'

# 9 - add route - to display all markets data where crops are sold
@app.route('/crop_market')
def crop_market():
    msg=""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM crop_market WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('crop_market.html', info=info, msg=msg)

        except Exception as e:
            print(f"crop_market Error: {e}")   
            msg = 'An error occurred during crop_market'

# delete route - to delete any entry or account
@app.route("/delete", methods = ['GET', 'POST'])
def delete():
    msg = ''
    if request.method == "POST":

        # getting value that will be deleted
        name = list(request.form)[0]
        value = request.form[name]
        column, table = name.split('+')
        print(request.form)

        # deleting value from respected table
        sql = "DELETE FROM " + table + " WHERE " + column + " = '" + value + "'"
        print(sql)
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                connection.commit()

                if (table != 'farmer'):
                    return redirect(table)

                # only user is deleted not data
                msg = 'User Deleted!!!'

            except Exception as e:
                print(f"Delete Error: {e}")   
                msg = 'An error occurred during delete'
    return render_template('login.html', msg = msg)

# update route - to get old data for update
@app.route("/update", methods = ['GET', 'POST'])
def update():
    msg = ''
    if request.method == 'POST':

        # Getting all old values to update them with new values 
        name = list(request.form.to_dict())[0]
        print("Request Form:", request.form)
        column_id = request.form[name]
        column, table = name.split('+')
        # print("column_id", column_id)

        # Construct the SQL query using parameterized queries to avoid SQL injection
        # print("table", column)
        sql = f"SELECT * FROM {table} WHERE {column} = %s"
        connection = get_db_connection()
        
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)

        with connection.cursor() as cursor:
            try:
                # Using parameterized query to pass the column_id safely
                cursor.execute(sql, (column_id,))
                result = cursor.fetchone()
                if result is None:
                    msg = 'No data found for the given id'
                    return render_template('login.html', msg=msg)

                #remove User_id from result
                result = dict(result)
                #remove id column
                del result['id']
                print(result)
                del result['User_id']
                data = {
                    'info': result,
                    'user_id': session.get('id'),
                    'table': table,
                    'id': column_id,
                    'column': column
                }
                # print(data.values())
                connection.commit()
                return render_template('update.html', **data)

            except Exception as e:
                print(f"Update Error: {e}")   
                msg = 'An error occurred during update'

    return render_template('login.html', msg=msg)


# update_confirm - to update with new data
@app.route("/update_confirm", methods = ["GET", "post"])
def update_confirm():
    msg = ""
    if request.method == "POST":

        # getting new data to update
        name = request.form.to_dict()
        table, column = list(name.keys())[-1].split('+')
        column_id = list(name.values())[-1]
        info = dict(list(name.items())[:-1])

        q1 = "UPDATE " + table
        q2 = " SET "
        for key, value in info.items():
            
            # to solve conversion error
            try:
                temp = float(value)
                if int(temp) / temp == 1 or temp / int(temp) > 1:
                    pass
            except ValueError:
                value = "'" + value + "'"
            q2 = q2 + key +" = " + value + ", "
        q2 = q2[:-2]
        q3 = " WHERE " + column + " = '" + column_id + "'"
        sql = q1 + q2 + q3

        # update old data with new data
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)
        with connection.cursor() as cursor:
            try: 
                cursor.execute(sql)
                connection.commit()
                return redirect(table)

            except Exception as e:
                print(f"Update Confirm Error: {e}")   
                msg = 'An error occurred during update_confirm'
    return render_template("login.html", msg = msg) 

# add route - to get table, column names to add
@app.route("/add", methods = ['GET', 'POST'])
def add():
    msg = ''
    if request.method == 'POST':

        # getting table, column name to add
        id_column = list(request.form.to_dict())[0]
        table = request.form[id_column]
        database_name = 'farm1_db'

        # Use string concatenation or f-string to correctly inject the database_name
        sql = f"SELECT column_name FROM information_schema.columns WHERE table_schema = '{database_name}' AND table_name = '{table}'"
        
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)

        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                all_columns = cursor.fetchall()  # No need to cast it to list
                data_columns = []
                # print(all_columns)
                # removing unwanted columns
                for column in all_columns:
                    if column["column_name"] not in [id_column, 'User_id']:
                        data_columns.append(column["column_name"])
                #remove id column
                data_columns.remove('id')
                data = {"columns": data_columns, "table": table, "user_id": session.get('id')}
                print(data)
                return render_template('add.html', **data)

            except Exception as e:
                print(f"Add Error: {e}")
                msg = 'An error occurred during add'

    return render_template('login.html', msg=msg)


# add_confirm - to add new data
@app.route("/add_confirm", methods = ['GET', 'POST'])
def add_confirm():
    msg = ''
    if request.method == 'POST':

        # Getting form data
        name = request.form.to_dict()
        table = list(name.keys())[-1]  # Table name is the last key
        temp = list(name.items())[:-1]  # Removing table name from data
        columns = dict(temp)

        # SQL query construction
        column_names = ", ".join(columns.keys()) + ", User_id"
        column_values = []

        # Prepare values for insertion and ensure proper quoting for non-numeric values
        for value in columns.values():
            try:
                # Check if the value is a number and handle it properly
                float_value = float(value)
                if int(float_value) == float_value:  # If it's an integer
                    column_values.append(str(int(float_value)))
                else:  # If it's a float
                    column_values.append(str(float_value))
            except ValueError:
                # Handle string values by enclosing in quotes
                column_values.append(f"'{value}'")

        # Add the user_id to the values
        column_values.append(f"'{session.get('id')}'")

        # Final SQL query construction
        sql = f"INSERT INTO {table} ({column_names}) VALUES ({', '.join(column_values)})"

        # Establish database connection
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)

        with connection.cursor() as cursor:
            try:
                cursor.execute(sql)
                connection.commit()  # Commit the transaction
                return redirect(table)  # Redirect to the appropriate table page
            except Exception as e:
                print(f"Add Confirm Error: {e}")
                msg = 'An error occurred during add_confirm'

    return render_template('login.html', msg=msg)


# to calulate sum
def calculate_total(d):
    total = 0
    for v in d:
        total += list(v.values())[0]
    return(total)

# profit_loss_overall route - to caluculate overall profit-loss
@app.route('/profit_loss_overall', methods=['GET', 'post'])
def profit_loss_overall():
    data = getProfitLoss()
    print(data)

    return render_template('profit.html', **data)

# cropwise route - give crop name to calculate profit-loss
@app.route('/cropwise', methods = ['GET', 'post'])
def cropwise():
    return render_template("cropwise.html", user_id = session['id'])

# profit_loss_cropwise - to calculate cropwise profit-loss 
@app.route('/profit_loss_cropwise', methods = ['GET', 'post'])
def profit_loss_cropwise():
    msg = ''
    if request.method == 'POST':
        crop_name = request.form['crop_name']
        print(crop_name)
        sp=0
        exp1=0
        exp2=0
        exp3=0
        exp4=0

        # getting selling prices of every crop and all expences and calculating its sum
        sql1 = "SELECT Selling_price FROM crop_market WHERE User_id = '" + str(session['id']) + "' " + "AND crop_name = '" + crop_name+ "'"
        
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)
        with connection.cursor() as cursor:
            try: 
                cursor.execute(sql1)
                sp = cursor.fetchall()
                sp = calculate_total(sp)

            except Exception as e:
                print(f"Profit Loss Error in crop_market: {e}")

        q1 = "SELECT seed_price FROM seed WHERE User_id = '" + str(session['id']) + "' " + " AND crop_name = '" + crop_name + "'"
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)
        with connection.cursor() as cursor:
            try: 
                cursor.execute(q1)
                exp1 = cursor.fetchall()
                exp1 = calculate_total(exp1)
            
            except Exception as e:
                print(f"Profit Loss Error in seed: {e}")
        
        
        q2 = "SELECT pesticide_price FROM pesticide WHERE User_id = '" + str(session['id']) + "' " + " AND crop_name = '" + crop_name + "'"
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)
        with connection.cursor() as cursor:
            try: 
                cursor.execute(q2)
                exp2 = cursor.fetchall()
                exp2 = calculate_total(exp2)
            except Exception as e:
                print(f"Profit Loss Error in pesticide: {e}")
        

        q3 = "SELECT fertilizer_price FROM fertilizer WHERE User_id = '" + str(session['id']) + "' " + " AND crop_name = '" + crop_name + "'"
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)
        with connection.cursor() as cursor:
            try: 
                cursor.execute(q3)
                exp3 = cursor.fetchall()
                exp3 = calculate_total(exp3)
            except Exception as e:
                print(f"Profit Loss Error in fertilizer: {e}")

        q4 = "SELECT salary FROM labour WHERE User_id = '" + str(session['id']) + "' "  + " AND crop_name = '" + crop_name + "'"
        connection = get_db_connection()
        if connection is None:
            msg = 'Database connection failed'
            return render_template('login.html', msg=msg)
        with connection.cursor() as cursor:
            try:
                cursor.execute(q4)
                exp4 = cursor.fetchall()
                exp4 = calculate_total(exp4)
            except Exception as e:
                print(f"Profit Loss Error: {e}")
                
        
        total_exp = exp1 + exp2 + exp3 + exp4
        values = [exp1, exp2, exp3, exp4]
        data = {'user_id': session['id'], 'msg': msg, 'values': values, 'total_exp': total_exp, 'sp': sp, 'color': 'primary'}

        if (sp - total_exp) > 0:
            data['color'] = '#2e7d32'
        elif (sp - total_exp) < 0:
            data['color'] = '#d32f2f'
        return render_template('profit.html', **data)
    return render_template('login.html', msg = msg)