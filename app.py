from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from pymongo import MongoClient
from dotenv import load_dotenv
from openai import OpenAI
import datetime
import bcrypt
import utils
import jwt
import os

app = Flask(__name__)

load_dotenv()

client = MongoClient(os.getenv('MONGO_URI'))
db = client['courses']
users_collection = db['users']
SECRET_KEY = os.getenv('JWT_SECRET')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

 
def chatComplete(key,text):
    client = OpenAI(
     api_key=key,
    )

    chat_completion = client.chat.completions.create(
         messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
        model="gpt-3.5-turbo",
    )
    response_content = chat_completion.choices[0].message.content
    return response_content
        

 # Signup route
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if the user already exists
        existing_user = users_collection.find_one({'username': username})
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Save the user to the database
        users_collection.insert_one({
            'username': username,
            'password': hashed_password.decode('utf-8')
        })
        
        return render_template('login.html')
    else:
        return render_template('signup.html')

# Login route
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user in MongoDB
        user = users_collection.find_one({'username': username})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Generate JWT token
            token = jwt.encode({
                'user_id': str(user['_id']),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, SECRET_KEY, algorithm='HS256')
            
            # Store the token in a cookie
            response = make_response(render_template('index.html'))
            response.set_cookie('jwt_token', token)
            return render_template('index.html')
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        return render_template('login.html')
 
# Home route (protected)
@app.route('/')
def home():
    return render_template('index.html')

# Prediction route
@app.route('/predict/', methods=['POST'])
def predict():
    # Extract input data from the form
    Gender = request.form.get('Gender')
    Married = request.form.get('Married')
    Education = request.form.get('Education')
    Self_Employed = request.form.get('Self_Employed')
    ApplicantIncome = request.form.get('ApplicantIncome')
    CoapplicantIncome = request.form.get('CoapplicantIncome')
    LoanAmount = request.form.get('LoanAmount')
    Loan_Amount_Term = request.form.get('Loan_Amount_Term')
    Credit_History = request.form.get('Credit_History')
    Property_Area = request.form.get('Property_Area')
    Dependents = request.form.get('Dependents')
    loanTerm= int(Loan_Amount_Term)
    # Call preprocessdata function
    prediction = utils.preprocessdata(
        Gender, Married, Education, Self_Employed, ApplicantIncome,
        CoapplicantIncome, LoanAmount, loanTerm*360, Credit_History,
        Property_Area, Dependents
    )

    response = chatComplete(OPENAI_API_KEY , f"Gender,Married,Education,Self_Employed,ApplicantIncome,CoapplicantIncome,LoanAmount,Loan_Amount_Term,Credit_History,Dependents, model-prediction:{prediction}, if model-prediction [0] means not approved if [1] means approved so response accordinglu , parameters:{Gender},{Married},{Education},{Self_Employed},{ApplicantIncome},{CoapplicantIncome},{LoanAmount},{Loan_Amount_Term},{Credit_History},{Dependents} ,task: give 2 liner reason for the prediction  ")
    # Assuming prediction is a list where the first element is the prediction result
    result=""
    if prediction[0] == 0:
        result = "Loan is not Approved"
    else:
        result = "Loan is Approved"
        
    return render_template('predict.html', prediction=result , response=response)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
