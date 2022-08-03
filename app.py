from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import json 
import web3tnx as w3
from random import randint as r
from flask_mail import Mail, Message

with open("info.json", "r") as c:
    parameters = json.load(c)["parameters"]

app = Flask(__name__)

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = parameters['gmail-user'],
    MAIL_PASSWORD=  parameters['gmail-password']
)

mail = Mail(app)

app.config['SQLALCHEMY_DATABASE_URI'] = parameters["database"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = parameters["track_modifications"]
app.config['SECRET_KEY'] = parameters["secret_key"] 

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(512), nullable = False)
    password = db.Column(db.String(512), nullable = False)
    user_addres = db.Column(db.String(512), nullable = False)
    user_priv_key = db.Column(db.String(512), nullable = False)
    user_email = db.Column(db.String(512), nullable = False)
    user_alert = db.Column(db.Float, nullable = False) 
    user_max_top = db.Column(db.Float, nullable = False)
    user_min_top = db.Column(db.Float, nullable = False)
    user_max = db.Column(db.Float, nullable = False)
    user_min = db.Column(db.Float, nullable = False)
    user_bal = db.Column(db.Float, nullable = False)
    user_base = db.Column(db.Float, nullable = False)
    usertrades = db.relationship('UserTrades', backref = 'user', lazy = True)

    def __repr__(self):
        return 'Id: ' + str(self.id) + ', Name: ' + self.name + '.'

class UserTrades(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime , nullable = False, default = datetime.utcnow())
    type_of_sale = db.Column(db.String(512), nullable = False)
    profit_margin = db.Column(db.Float, nullable = False)
    hash_returend = db.Column(db.String(512), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    def __repr__(self):
        return 'Id: ' + str(self.id) + ', User_id' + str(self.user_id)


class Blockkey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    addres_key = db.Column(db.String(512), nullable=False)
    private_key = db.Column(db.String(512), nullable=False)

    def __repr__(self):
        return self.addres_key


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Global Variables
# n = 5
account_reciver_admin = parameters["account_reciver_admin"]
private_key_admin = parameters["private_key_admin"]


# def payments(addres_key, account_reciver, private_key, value):
#     gas = 20000
#     hash_returned = w3.make_transaction(addres_key, account_reciver, private_key, value, gas)
#     return hash_returned

# def send_mail():
#     return "YAY"  


@app.route('/', methods = ['GET', 'POST'])
@login_required
def index():
    trades = current_user.usertrades
    return render_template('index.html', current_user = current_user, trades = trades)
    


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_password = w3.SHA256(request.form.get('user_password'))
        
        x = User.query.filter_by(name = user_name)[0]

        if x.name == user_name and x.password == user_password:
            user = User.query.get(x.id)
            load_user(user.id)
            login_user(user)
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        user_password = w3.SHA256(request.form.get('user_password'))
        user_alert = float(request.form.get('user_alert'))
        user_bal = r(1000, 10000)
        user_base = w3.get_val_eth(False)
        user_max, user_min, user_max_top, user_min_top = 1.1, 0.98, 1.5, 0.9
        
        blockkey = Blockkey.query.all()[0]
        
        user = User(name = user_name, 
                    password = user_password, 
                    user_addres = blockkey.addres_key, 
                    user_priv_key = blockkey.private_key,
                    user_email = user_email,
                    user_alert = user_alert,
                    user_bal = user_bal,
                    user_max = user_max,
                    user_min = user_min,
                    user_max_top = user_max_top,
                    user_min_top = user_min_top,
                    user_base = user_base)
        
        block_remove = Blockkey.query.get_or_404(blockkey.id)
        
        db.session.delete(block_remove)
        db.session.add(user)
        db.session.commit()
        
        x = User.query.filter_by(name = user_name)[0]
        
        if x.name == user_name and x.password == user_password:
            user = User.query.get(x.id)
            load_user(user.id)
            login_user(user)
            return redirect(url_for('index'))
            
    return redirect(url_for('login'))



@app.route('/signout', methods = ['GET', 'POST'])
@login_required
def signout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/makepayment', methods = ['GET', 'POST'])
@login_required
def makepayment():
    if request.method == 'POST':
        account_reciver = request.form.get('account_reciver')
        user_password = w3.SHA256(request.form.get('user_password'))
        
        value = float(request.form.get('value'))

        if user_password == current_user.user_password and value <= current_user.user_bal:
            current_user.user_bal -= float(value)
            hash_returned = w3.make_transacti(current_user.user_addres, account_reciver, current_user.user_priv_key, value)
            return render_template('index.html', user = current_user, hash_returned = hash_returned)

    return render_template('index.html', user = current_user)



@app.route('/api/buy', methods = ['GET', 'POST'])
@login_required
def buy_crypt():
    if request.method == 'POST':
        value = float(request.form.get('value'))
        user_password = w3.SHA256(request.form.get('user_password'))
        value_eth = w3.get_val_eth(value)
        
        if user_password == current_user.password and value <= current_user.user_bal:
            current_user.user_bal -= value
            hash_returned = w3.make_transaction(account_sender = account_reciver_admin,
                                                account_reciver = current_user.user_addres,
                                                private_key = private_key_admin,
                                                value = value_eth, 
                                                gas = 200000)

            trade = UserTrades(type_of_sale = "Buying Crypto for user " + str(current_user.user_addres),
                               profit_margin = 0.0,
                               hash_returend = hash_returned,
                               user_id = current_user.id)
            
            db.session.add(trade)
            db.session.commit()
            
            return render_template('buy.html', msg = str(value_eth) + ' worth eather bought!!')
            
    return render_template('buy.html')


@app.route('/api/sell', methods = ['GET', 'POST'])
@login_required
def sell_crypt():
    if request.method == 'POST':
        value = float(request.form.get('value'))
        user_password = w3.SHA256(request.form.get('user_password'))
        value_eth = w3.get_val_eth(value)
        
        if user_password == current_user.user_password and value <= current_user.user_bal:
            current_user.user_bal += value
            hash_returned = w3.make_transaction(account_sender = current_user.user_addres,
                                                account_reciver = account_reciver_admin,
                                                private_key = current_user.user_priv_key,
                                                value = value_eth, 
                                                gas = 200000)

            trade = UserTrades(type_of_sale = "Buying Crypto for user " + str(current_user.user_addres),
                               profit_margin = 0.0,
                               hash_returend = hash_returned,
                               user_id = current_user.id)
            
            db.session.add(trade)
            db.session.commit()
            
            return render_template('buy.html', msg = str(value_eth) + ' worth eather bought!!')
            
    return render_template('buy.html')


@app.route('/api/create/alert/', methods = ['GET'])
@login_required
def create_alert():
    if request.method == 'POST':
        alert = request.form.get('alert')
        current_user.alert = float(alert)
        db.session.commit()
        return "Alert Edited!!"
    return render_template('alert.html')


@app.route('/api/modify/alert/', methods = ['GET'])
@login_required
def modify_alert():
    if request.method == 'POST':
        alert = request.form.get('alert')
        current_user.alert = float(alert)
        db.session.commit()
        return "Alert Edited!!"
    return render_template('alert.html')


@app.route('/api/delete/alert/', methods = ['GET'])
@login_required
def delete_alert():
    if request.method == 'POST':
        alert = request.form.get('alert')
        current_user.alert = float(alert)
        db.session.commit()
        return "Alert Deleted!!"
    return render_template('alert.html')
    

@app.route('/api/info/user/<x>', methods = ['GET', 'POST'])
def api_info_user(x):
    if request.method == 'GET':
        pos_users = User.query.filter_by(user_addres = str(x))[0]
        if pos_users.user_addres == str(x):
            user = User.query.get(pos_users.id)
            load_user(user.id)
            login_user(user)
            dict = {}
            dict['name'] = current_user.name
            dict['password'] = current_user.password
            dict['user_addres'] = current_user.user_addres
            dict['user_priv_key'] = current_user.user_priv_key
            dict['user_alert'] = current_user.user_priv_key
            dict['user_bal'] = current_user.user_priv_key
            dict['user_max'] = current_user.user_priv_key
            dict['user_max_top'] = current_user.user_priv_key
            dict['user_min_top'] = current_user.user_priv_key
        return jsonify(dict)
    
    return('Request Denied')


@app.route('/api/algo/trade/<x>/', methods = ['GET'])
def api_algo_trade(x):
    if request.method == 'GET':
        pos_users = User.query.filter_by(user_addres = str(x))[0]
        if pos_users.user_addres == x:
            user = User.query.get(pos_users.id)
            load_user(user.id)
            login_user(user)
            
            acc_bal = float(w3.get_acc_bal(current_user.user_addres))
            eth_val = w3.get_val_eth(False)
            acc_bal_eth = acc_bal * eth_val
            acc_bal_bought = acc_bal * current_user.user_base
            hash_returned = ''

            
            user_max_top = (current_user.user_max_top)*acc_bal_bought
            user_min_top = (current_user.user_min_top)*acc_bal_bought
            user_max = (current_user.user_max)* acc_bal_bought
            user_min = (current_user.user_min)*acc_bal_bought
            
            print('acc_bal_eth = ' + str(acc_bal_eth))
            print('acc_bal_bought = ' + str(acc_bal_bought))
            print('acc_bal = ' + str(acc_bal))
            print('user_max_top = ' + str(user_max_top) + " " + str(current_user.user_max_top))
            print('user_min_top = ' + str(user_min_top) + " " + str(current_user.user_min_top))
            print('user_max = ' + str(user_max) + " " + str(current_user.user_max))
            print('user_min = ' + str(user_min) + " " + str(current_user.user_min))
            
            if acc_bal_bought >= user_max_top:
                print("acc_bal >= user_max_top")
                hash_returned = w3.make_transaction(account_sender = current_user.user_addres,
                                                    account_reciver = account_reciver_admin,
                                                    private_key = current_user.user_priv_key,
                                                    value = (acc_bal*0.98), 
                                                    gas = 200000)
                
                
            elif acc_bal_bought <= user_min_top:
                print("acc_bal <= user_min_top")
                hash_returned = w3.make_transaction(account_sender = current_user.user_addres,
                                                    account_reciver = account_reciver_admin,
                                                    private_key = current_user.user_priv_key,
                                                    value = (acc_bal*0.98), 
                                                    gas = 200000)
                
            elif acc_bal_bought >= user_max:
                print("cc_bal >= user_max")
                hash_returned = w3.make_transaction(account_sender = current_user.user_addres,
                                                    account_reciver = account_reciver_admin,
                                                    private_key = current_user.user_priv_key,
                                                    value = (acc_bal*0.39),
                                                    gas = 200000)
                
            elif acc_bal_bought <= user_min:
                print("acc_bal <= user_min")
                hash_returned = w3.make_transaction(account_sender = current_user.user_addres,
                                                    account_reciver = account_reciver_admin,
                                                    private_key = current_user.user_priv_key,
                                                    value = (acc_bal*0.39),
                                                    gas = 200000)
                
            elif acc_bal_eth == acc_bal_bought:
                print("acc_bal == acc_bal")
                print((acc_bal*0.29))
                hash_returned = w3.make_transaction(account_sender = account_reciver_admin,
                                                    account_reciver = current_user.user_addres,
                                                    private_key = private_key_admin,
                                                    value = (acc_bal*0.29),
                                                    gas = 200000)
            
            if hash_returned:
                trade = UserTrades(type_of_sale = "Trading Crypto for user " + str(current_user.user_addres),
                                   profit_margin = 0.0,
                                   hash_returend = hash_returned,
                                   user_id = current_user.id)
            
                db.session.add(trade)
                db.session.commit()

            return jsonify({200: 'YaY!'})
        
    return "Failed"
 
 
            
@app.route('/api/check/<x>/', methods = ['GET'])
def api_algo_check(x):
    if request.method == 'GET':
        pos_users = User.query.filter_by(user_addres = str(x))[0]
        if pos_users.user_addres == x:
            user = User.query.get(pos_users.id)
            load_user(user.id)
            login_user(user)

            if current_user.user_alert >= w3.get_val_eth(False):
                msg = "The value of ether that you had set for " + str(current_user.user_alert) + " has changed to " + str(w3.get_val_eth(False)) + ". Keep Trading!!"
                email = current_user.user_email 
                mail.send_message(subject='Alert Crpto Price Changed!!',
                                  sender = email,
                                  recipients = [parameters['gmail-user']],
                                  body = msg)
                return render_template('Msg Sent' + str(msg))

if __name__ == '__main__':
    app.run(debug = True, threaded = True)