# # from flask import Flask, render_template, request, redirect, url_for, session
# from flask_mysqldb import MySQL
# import pymysql

# app = Flask(__name__)

# # MySQL database configuration
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'farm1_db'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# # Explicitly install pymysql as MySQLdb
# pymysql.install_as_MySQLdb()

# # Initialize MySQL connection
# mysql = MySQL(app)

  
# routes  
# login route
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = 'your secret key'

# Database connection function
def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
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
                cursor.execute('SELECT * FROM farmer WHERE User_id = %s AND Password = %s', (username, password))
                account = cursor.fetchone()

                if account:
                    # if account found then log in successful
                    session['loggedin'] = True
                    session['id'] = account['User_id'] 
                    msg = 'Logged in successfully!!!'   
                
                    if account['F_Firstname'] == '' and account['F_Lastname'] == '':
                        # if firstname and lastname is none or empty and then complete profile
                        msg = "complete your profile"
                        return render_template("complete.html")
                    
                    # getting farmer info where id and password matches
                    cursor.execute('SELECT * FROM farmer WHERE User_id = %s', (session['id'],)) 
                    info = cursor.fetchone()
                    data = {'user_id': session['id'], 'msg': msg, 'info': info}

                    # displaying farmer basic info 
                    return render_template('index.html', **data)
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
        user_id = request.form['username'] 
        password = request.form['password']
        
        # Establish database connection
        connection = get_db_connection()
        
        if connection is None:
            msg = 'Database connection failed'
            return render_template('signup.html', msg=msg)
        
        try:
            with connection.cursor() as cursor:
                # check if user already exists
                cursor.execute('SELECT * FROM farmer WHERE User_id = %s', (user_id, )) 
                account = cursor.fetchone() 
                
                if account:
                    # if user already exists then displaying error
                    msg = 'Account already exists!!!'
                else: 
                    # if user doesn't exist then create new user
                    cursor.execute('INSERT INTO farmer (F_Firstname, F_Lastname, F_Email, F_Phone, F_Income, User_id, Password) VALUES ("", "", "", "", 0, %s, %s)', (user_id, password)) 
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
                    'UPDATE farmer SET F_Firstname=%s, F_Lastname=%s, F_Gender=%s, F_Address=%s, F_ContactNo=%s WHERE User_id=%s',
                    (first, last, gender, address, contact, user_id)
                )
                connection.commit()

                # Fetch updated user info
                cursor.execute('SELECT * FROM farmer WHERE User_id = %s', (user_id,))
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


# from now 9 routes are used for displaying respected data and if no data found then display error
# 1 - home route - to main user page
@app.route('/home')
def home():
    msg = ""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM farmer WHERE User_id = %s ', (session['id'],)) 
            info = cursor.fetchone()
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('index.html', **data)

    except Exception as e:
        print(f"Home Error: {e}")
        msg = 'An error occurred during home'
    # return render_template('index.html', msg=msg)

# 2 - farm route - to display farm data
@app.route('/farm')
def farm():
    msg=""
    connection = get_db_connection()
    if connection is None:
        msg = 'Database connection failed'
        return render_template('index.html', msg=msg)
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM farm WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            for d in info:
                _ = d.popitem()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('farm.html', **data)

        except Exception as e:
            print(f"Farm Error: {e}")   
            msg = 'An error occurred during farm'

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
            for d in info:
                _ = d.popitem()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
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
            for d in info:
                _ = d.popitem()
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
            for d in info:
                _ = d.popitem()
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
            for d in info:
                _ = d.popitem()
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
    with connection.cursor() as cursor:
        try:
            cursor.execute('SELECT * FROM labour WHERE User_id = %s ', (session['id'],))
            info = cursor.fetchall()
            for d in info:
                _ = d.popitem()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('labour.html', **data)

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
            for d in info:
                _ = d.popitem()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('warehouse.html', **data)

        except Exception as e:
            print(f"warehouse Error: {e}")   
            msg = 'An error occurred during warehouse'

# 9 - crop_market route - to display all markets data where crops are sold
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
            for d in info:
                _ = d.popitem()
            if len(info)==0:
                msg="Sorry, no data found!!!"
            data = {'user_id': session['id'], 'msg': msg, 'info': info}
            return render_template('crop_market.html', **data)

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
        print("column_id", column_id)

        # Construct the SQL query using parameterized queries to avoid SQL injection
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

                # Remove the User_id from the data, if present
                temp = list(result.items())[1:-1]  # Removing the first and last elements (User_id and other unnecessary fields)
                info = dict(temp)

                # Prepare the data to send to the template
                data = {
                    'info': info,
                    'user_id': session.get('id'),
                    'table': table,
                    'id': column_id,
                    'column': column
                }
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
                print(all_columns)
                # removing unwanted columns
                for column in all_columns:
                    if column["column_name"] not in [id_column, 'User_id']:
                        data_columns.append(column["column_name"])

                data = {"columns": data_columns, "table": table, "user_id": session.get('id')}
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
    msg=''

    # getting selling prices of every crop and all expences and calculating its sum
    sql1 = "SELECT selling_price FROM crop_market WHERE User_id = '" + session['id'] + "' "
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

    
    q1 = "SELECT seed_price FROM seed WHERE User_id = '" + session['id'] + "' "  
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
    
    q2 = "SELECT pesticide_price FROM pesticide WHERE User_id = '" + session['id'] + "' "
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

    q3 = "SELECT fertilizer_price FROM fertilizer WHERE User_id = '" + session['id'] + "' "
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

    q4 = "SELECT salary FROM labour WHERE User_id = '" + session['id'] + "' "
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
        data['color'] = 'success'
    elif (total_sp - total_exp) < 0:
        data['color'] = 'danger'

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

        # getting selling prices of every crop and all expences and calculating its sum
        sql1 = "SELECT selling_price FROM crop_market WHERE User_id = '" + session['id'] + "' " + " AND crop_name = '" + crop_name + "' "
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
                print(f"Profit Loss Error: {e}")

        q1 = "SELECT seed_price FROM seed WHERE User_id = '" + session['id'] + "' " + " AND crop_name = '" + crop_name + "' " 
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
        
        
        q2 = "SELECT pesticide_price FROM pesticide WHERE User_id = '" + session['id'] + "' " + " AND crop_name = '" + crop_name + "' "
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
        

        q3 = "SELECT fertilizer_price FROM fertilizer WHERE User_id = '" + session['id'] + "' " + " AND crop_name = '" + crop_name + "' "
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
        
        total_exp = exp1 + exp2 + exp3
        values = [exp1, exp2, exp3]
        data = {'user_id': session['id'], 'msg': msg, 'values': values, 'total_exp': total_exp, 'sp': sp, 'color': 'primary'}

        if (sp - total_exp) > 0:
            data['color'] = 'success'
        elif (sp - total_exp) < 0:
            data['color'] = 'danger'
        return render_template('profit.html', **data)
    return render_template('login.html', msg = msg)