from flask import Flask, request, jsonify, abort, session
app = Flask(__name__)
app.config['DEBUG'] = True
from google.appengine.ext import ndb
import json
import db_defs

"""
This program borrows code from the "Designing a RESTFUL 
API with Python and Flask" tutorial by Miguel Grinberg 
(http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask).
It also borrows code from the Week 4 Lectures of CS496.
"""

app.secret_key = 'DONOTUSE' # Generate a secret, random key

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    if 'username' in session:
        return 'Logged in as %s' % session['username']
    else:
        return "Hello World!"

@app.route('/api/forsale/register', methods=['POST'])
def register():
    if not request.json:
        return "Error: API only supports application/json MIME type\n\n", 406
       
    new_user = db_defs.Account()
    email = request.json.get('email')
    password = request.json.get('password')
    nickname = request.json.get('nickname')
    
    if 'email' in request.json:
        new_user.email = email
        existing_user = db_defs.Account.query(db_defs.Account.email==email).get()
        if existing_user:
            return "Error: This email is already in use\n\n", 400
    else:
        return "Error: each user must provide an email\n\n", 400
        
    if 'password' in request.json:
        new_user.password = password
    else:
        return "Error: each user must provide a password\n\n", 400
    
    if 'nickname' in request.json:
        new_user.nickname = nickname
    else:
        return "Error: each user must provide a nickname\n\n", 400
        
    key = new_user.put() 
    out = new_user.to_dict()
    return jsonify(out)
     
@app.route('/api/forsale/login', methods=['POST', 'GET'])
def login():
    if not request.json:
        return "Error: API only supports application/json MIME type\n\n", 406
    
    if request.method == 'POST':
        email = request.json.get('email')
        password = request.json.get('password')
        
        user = db_defs.Account.query(db_defs.Account.email==email).get()
        if user.password == password:
            session['username'] = email
            return jsonify({"user":session['username']})
        else:
            return "Error: Invalid username or password\n\n", 400
        
@app.route('/logout')
def logout():
    session.pop('username', None)
    
@app.route('/api/forsale', methods=['POST'])
def add_item():
    if not request.json:
        return "Error: API only supports application/json MIME type\n\n", 406
        
    new_item = db_defs.Item()
    name = request.json.get('name')
    price = request.json.get('price')
    description = request.json.get('description')
    location = request.json.get('location')
    if 'username' in session:
        seller = session['username']
    else:
        return "Error: User not logged in\n\n", 406
    
    if 'name' in request.json:
        new_item.name = name
    else:
        return "Error: Each item must have a name\n\n", 400
        
    if description:
        new_item.description = description
        
    if 'price' in request.json:
        new_item.price = int(price)
    else:
        return "Error: Each item must have a price\n\n", 400
        
    if 'location' in request.json:
        new_item.location = location
    else:
        return "Error: Each item must have a location\n\n", 400
        
    if seller:
        new_item.seller = seller
    else:
        return "Error: Each item must have a seller\n\n", 400
        
    key = new_item.put() 
    out = new_item.to_dict()
    return jsonify(out) 

@app.route('/api/forsale', methods=['GET'])
def view_item_keys():
    q = db_defs.Item.query()
    keys = q.fetch(keys_only=True)
    results = {'keys': [x.id() for x in keys]}
    return jsonify(results)
    
@app.route('/api/forsale/myitems', methods=['GET'])
def view_specific_keys():
    if 'username' in session:
        q = db_defs.Item.query(db_defs.Item.seller==session['username'])
        keys = q.fetch(keys_only=True)
        results = {'keys': [x.id() for x in keys]}
        return jsonify(results)
    else:
        return "Error: User not logged in\n\n", 406
    
@app.route('/api/forsale/<int:item_id>', methods=['GET'])
def view_item(item_id):
    out = ndb.Key(db_defs.Item, item_id).get().to_dict() 
    return jsonify(out)    
    
@app.route('/api/forsale/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if not request.json:
        return "Error: API only supports application/json MIME type\n\n", 406
        
    current_item = ndb.Key(db_defs.Item, item_id).get()
    if 'username' in session:
        if current_item.seller == session['username']:
            pass
        else:
            return "Error: Item not associated with user\n\n", 406
        
    name = request.json.get('name')
    price = request.json.get('price')
    description = request.json.get('description')
    location = request.json.get('location')
    
    if name:
        current_item.name = name
    if price:
        current_item.price = int(price)
    if description:
        current_item.description = description
    if location:
        current_item.location = location

    key = current_item.put() 
    out = current_item.to_dict()
    return jsonify(out) 
    
@app.route('/api/forsale/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    current_item = ndb.Key(db_defs.Item, item_id).get()
    if 'username' in session:
        if current_item.seller == session['username']:
            pass
        else:
            return "Error: Item not associated with user\n\n", 406
            
    current_item.key.delete()
    return "\nDeleted item\n\n"
    
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
    
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE, OPTIONS')
    return response
    