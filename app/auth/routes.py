# app/auth/routes.py
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from functools import wraps
from ..database.mongo import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Helper function to require authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
            db = get_db()
            current_user = db.users.find_one({'_id': data['user_id']})
            
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
                
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
            
        return f(*args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields!'}), 400
        
    db = get_db()
    
    # Check if user already exists
    if db.users.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists!'}), 409
        
    # Create new user
    hashed_password = generate_password_hash(data['password'])
    
    new_user = {
        'email': data['email'],
        'password': hashed_password,
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'phone_number': data.get('phone_number'),
        'created_at': datetime.datetime.utcnow(),
        'last_login': None
    }
    
    result = db.users.insert_one(new_user)
    
    return jsonify({
        'message': 'User created successfully!',
        'user_id': str(result.inserted_id)
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password!'}), 400
        
    db = get_db()
    
    user = db.users.find_one({'email': data['email']})
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401
        
    # Update last login time
    db.users.update_one(
        {'_id': user['_id']},
        {'$set': {'last_login': datetime.datetime.utcnow()}}
    )
    
    # Generate JWT token
    secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_development_only')
    token = jwt.encode({
        'user_id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, secret_key, algorithm="HS256")
    
    return jsonify({
        'message': 'Login successful!',
        'token': token,
        'user_id': str(user['_id']),
        'email': user['email']
    })

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    user = g.current_user
    
    # Remove sensitive information
    user.pop('password', None)
    user['_id'] = str(user['_id'])
    
    return jsonify(user)
