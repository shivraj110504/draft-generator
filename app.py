"""
NyaySetu Flask Backend API
Production-ready API for legal document generation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from datetime import datetime
import json

from rti_generator import RTIGenerator
from affidavit_generator_backend import AffidavitGenerator
from orchestrator import DocumentOrchestrator
from database import NyaySetuDB

# Configuration
raw_origins = os.environ.get('ALLOWED_ORIGINS', '*')
# Split by comma, strip whitespace, and strip trailing slashes for robust matching
allowed_origins = [origin.strip().rstrip('/') for origin in raw_origins.split(',')]
print(f"CORS Allowed Origins (cleaned): {allowed_origins}")

app = Flask(__name__)
# Enable CORS for all /api/ routes with support for credentials and common headers
CORS(app, resources={r"/api/*": {
    "origins": allowed_origins,
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'outputs')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Ensure outputs directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
print(f"Upload Folder initialized at: {app.config['UPLOAD_FOLDER']}")

# Initialize generators and DB
rti_generator = RTIGenerator()
affidavit_generator = AffidavitGenerator()
orchestrator = DocumentOrchestrator()
db = NyaySetuDB()


@app.route('/')
def home():
    """API health check"""
    return jsonify({
        'status': 'success',
        'message': 'NyaySetu API v2.0',
        'endpoints': {
            'analyze': '/api/analyze',
            'generate_rti': '/api/generate/rti',
            'generate_affidavit': '/api/generate/affidavit',
            'download': '/api/download/<filename>',
            'states': '/api/states'
        },
        'database': 'connected' if db.client is not None else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_requirement():
    """
    Analyze user requirement and suggest document type
    Request: {"description": "I need RTI for exam records"}
    Response: {document_type, complexity_score, suggestions}
    """
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Description is required'
            }), 400
        
        analysis = orchestrator.analyze_requirements(data['description'])
        
        return jsonify({
            'status': 'success',
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/generate/rti', methods=['POST'])
def generate_rti():
    """
    Generate RTI Application
    Request: {name, address, state, authority, info, bpl, ...}
    Response: {pdf_url, hash, reference_number, validation}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'address', 'state', 'authority', 'pio_address', 'info']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Generate RTI document
        result = rti_generator.generate(data)
        
        # Store in "blockchain" database
        db.store_document(
            doc_type="RTI_APPLICATION",
            user_data=data,
            pdf_path=result['pdf_file'],
            doc_hash=result['document_hash'],
            ref_num=result['reference_number']
        )
        
        # Get relative file path for download
        filename = os.path.basename(result['pdf_file'])
        
        return jsonify({
            'status': 'success',
            'document': {
                'filename': filename,
                'download_url': f'/api/download/{filename}',
                'hash': result['document_hash'],
                'reference_number': result['reference_number'],
                'validation': result['validation']
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/generate/affidavit', methods=['POST'])
def generate_affidavit():
    """
    Generate Affidavit
    Request: {deponent_name, father_name, age, address, statements, ...}
    Response: {pdf_url, hash}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['deponent_name', 'address', 'statements']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'status': 'error',
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Generate affidavit
        result = affidavit_generator.generate(data)
        
        # Store in "blockchain" database
        db.store_document(
            doc_type="AFFIDAVIT",
            user_data=data,
            pdf_path=result['pdf_file'],
            doc_hash=result['document_hash']
        )
        
        filename = os.path.basename(result['pdf_file'])
        
        return jsonify({
            'status': 'success',
            'document': {
                'filename': filename,
                'download_url': f'/api/download/{filename}',
                'hash': result['document_hash']
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated PDF"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            print(f"ERROR: File not found at {file_path}")
            return jsonify({
                'status': 'error',
                'message': 'File not found'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/states', methods=['GET'])
def get_states():
    """Get list of supported states with rules"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'jurisdiction_rules.json')
        
        with open(config_path, 'r') as f:
            rules = json.load(f)
        
        states = []
        for state, info in rules.items():
            states.append({
                'name': state,
                'fee': info.get('fee'),
                'bpl_waiver': info.get('bpl_fee_waiver'),
                'languages': info.get('languages_accepted', [])
            })
        
        return jsonify({
            'status': 'success',
            'states': states
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/complexity', methods=['POST'])
def calculate_complexity():
    """Calculate complexity score for document"""
    try:
        data = request.get_json()
        
        score = orchestrator.calculate_complexity_score(data)
        
        return jsonify({
            'status': 'success',
            'complexity': score
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)
