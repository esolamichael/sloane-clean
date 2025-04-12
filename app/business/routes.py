# app/business/routes.py
from flask import Blueprint, request, jsonify, g
from bson.objectid import ObjectId
import datetime
from ..auth.routes import token_required
from ..database.mongo import get_db

business_bp = Blueprint('business', __name__, url_prefix='/api/business')

@business_bp.route('/', methods=['POST'])
@token_required
def create_business():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'message': 'Business name is required!'}), 400
    
    db = get_db()
    
    # Create new business profile
    new_business = {
        'owner_id': str(g.current_user['_id']),
        'name': data['name'],
        'description': data.get('description'),
        'phone_number': data.get('phone_number'),
        'email': data.get('email'),
        'website_url': data.get('website_url'),
        'address': data.get('address'),
        'city': data.get('city'),
        'state': data.get('state'),
        'zip_code': data.get('zip_code'),
        'country': data.get('country', 'United States'),
        'timezone': data.get('timezone', 'America/New_York'),
        'business_hours': data.get('business_hours', {}),
        'created_at': datetime.datetime.utcnow(),
        'updated_at': datetime.datetime.utcnow(),
        'subscription_active': False,
        'google_business_id': data.get('google_business_id'),
        'google_place_id': data.get('google_place_id')
    }
    
    result = db.businesses.insert_one(new_business)
    
    # Return the new business with ID
    new_business['_id'] = str(result.inserted_id)
    
    return jsonify(new_business), 201

@business_bp.route('/', methods=['GET'])
@token_required
def get_user_businesses():
    db = get_db()
    
    # Get all businesses owned by the current user
    businesses = list(db.businesses.find({'owner_id': str(g.current_user['_id'])}))
    
    # Convert ObjectIDs to strings for JSON serialization
    for business in businesses:
        business['_id'] = str(business['_id'])
    
    return jsonify(businesses)

@business_bp.route('/<business_id>', methods=['GET'])
@token_required
def get_business(business_id):
    db = get_db()
    
    # Get specific business and verify ownership
    business = db.businesses.find_one({
        '_id': ObjectId(business_id),
        'owner_id': str(g.current_user['_id'])
    })
    
    if not business:
        return jsonify({'message': 'Business not found or access denied!'}), 404
    
    # Convert ObjectID to string for JSON serialization
    business['_id'] = str(business['_id'])
    
    return jsonify(business)

@business_bp.route('/<business_id>', methods=['PUT'])
@token_required
def update_business(business_id):
    data = request.get_json()
    db = get_db()
    
    # Verify business exists and user owns it
    business = db.businesses.find_one({
        '_id': ObjectId(business_id),
        'owner_id': str(g.current_user['_id'])
    })
    
    if not business:
        return jsonify({'message': 'Business not found or access denied!'}), 404
    
    # Update fields (only allowing specific fields to be updated)
    update_data = {}
    allowed_fields = [
        'name', 'description', 'phone_number', 'email', 'website_url',
        'address', 'city', 'state', 'zip_code', 'country', 'timezone',
        'business_hours', 'google_business_id', 'google_place_id'
    ]
    
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
    
    # Add updated timestamp
    update_data['updated_at'] = datetime.datetime.utcnow()
    
    # Update in database
    db.businesses.update_one(
        {'_id': ObjectId(business_id)},
        {'$set': update_data}
    )
    
    # Get updated business
    updated_business = db.businesses.find_one({'_id': ObjectId(business_id)})
    updated_business['_id'] = str(updated_business['_id'])
    
    return jsonify(updated_business)

@business_bp.route('/<business_id>/website-data', methods=['POST'])
@token_required
def store_website_data(business_id):
    data = request.get_json()
    db = get_db()
    
    # Verify business exists and user owns it
    business = db.businesses.find_one({
        '_id': ObjectId(business_id),
        'owner_id': str(g.current_user['_id'])
    })
    
    if not business:
        return jsonify({'message': 'Business not found or access denied!'}), 404
    
    # Add business ID and timestamp to scraped data
    website_data = {
        'business_id': business_id,
        'url': data.get('url'),
        'content': data.get('content', {}),
        'sections': data.get('sections', []),
        'metadata': data.get('metadata', {}),
        'last_scraped': datetime.datetime.utcnow()
    }
    
    # Store website data in MongoDB
    result = db.website_data.insert_one(website_data)
    
    # Update business record with reference to latest scraped data
    db.businesses.update_one(
        {'_id': ObjectId(business_id)},
        {'$set': {'website_data_id': str(result.inserted_id)}}
    )
    
    return jsonify({
        'message': 'Website data stored successfully',
        'document_id': str(result.inserted_id)
    })

@business_bp.route('/<business_id>/google-business-data', methods=['POST'])
@token_required
def store_google_business_data(business_id):
    data = request.get_json()
    db = get_db()
    
    # Verify business exists and user owns it
    business = db.businesses.find_one({
        '_id': ObjectId(business_id),
        'owner_id': str(g.current_user['_id'])
    })
    
    if not business:
        return jsonify({'message': 'Business not found or access denied!'}), 404
    
    # Add business ID and timestamp to GBP data
    gbp_data = {
        'business_id': business_id,
        'google_place_id': data.get('google_place_id'),
        'business_name': data.get('business_name'),
        'description': data.get('description'),
        'address': data.get('address'),
        'phone_number': data.get('phone_number'),
        'categories': data.get('categories', []),
        'services': data.get('services', []),
        'hours': data.get('hours', {}),
        'photos_urls': data.get('photos_urls', []),
        'reviews': data.get('reviews', []),
        'attributes': data.get('attributes', {}),
        'last_updated': datetime.datetime.utcnow()
    }
    
    # Store GBP data in MongoDB
    result = db.google_business_profiles.update_one(
        {'business_id': business_id},
        {'$set': gbp_data},
        upsert=True
    )
    
    # Update business record with reference to GBP data
    if result.upserted_id:
        db.businesses.update_one(
            {'_id': ObjectId(business_id)},
            {'$set': {'gbp_data_id': str(result.upserted_id)}}
        )
    
    return jsonify({
        'message': 'Google Business Profile data stored successfully',
        'operation': 'inserted' if result.upserted_id else 'updated'
    })
