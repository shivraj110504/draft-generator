"""
NyaySetu - Smart Legal Validation System
Features:
- Pre-generation validation prevents legally invalid documents
- Context-aware validation rules
- Date consistency checking
- Automatic legal compliance detection
- Intelligent suggestions for improvement
"""

import re
import json
import os
from datetime import datetime, timedelta


class SmartLegalValidator:
    """Advanced validation with legal intelligence"""
    
    # Valid Indian states
    INDIAN_STATES = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
        'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
        'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
        'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
        'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
        'Delhi', 'Jammu and Kashmir', 'Ladakh'
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.blocking_issues = []  # Issues that prevent generation
        self.suggestions = []
        
        # Load jurisdiction data
        self.load_jurisdiction_profiles()
        self.load_rti_categories()
    
    def load_jurisdiction_profiles(self):
        """Load jurisdiction profiles"""
        try:
            profiles_path = os.path.join(os.path.dirname(__file__), 'jurisdiction_profiles.json')
            with open(profiles_path, 'r') as f:
                self.jurisdictions = json.load(f)
        except:
            self.jurisdictions = {}
    
    def load_rti_categories(self):
        """Load RTI categories"""
        try:
            cat_path = os.path.join(os.path.dirname(__file__), 'rti_categories.json')
            with open(cat_path, 'r') as f:
                self.rti_categories = json.load(f)
        except:
            self.rti_categories = {}
    
    def reset(self):
        """Reset validation results"""
        self.errors = []
        self.warnings = []
        self.blocking_issues = []
        self.suggestions = []
    
    def validate_rti_application(self, user_data):
        """Smart validation for RTI applications"""
        self.reset()
        
        # Basic required fields
        required_fields = ['name', 'address', 'state', 'authority', 'pio_address', 'info']
        for field in required_fields:
            if not user_data.get(field) or not str(user_data[field]).strip():
                self.errors.append(f"❌ Missing required field: {field}")
        
        # If basic validation fails, return early
        if self.errors:
            return False
        
        # Name validation
        self._validate_name(user_data['name'], 'Applicant Name')
        
        # Address validation
        self._validate_address(user_data['address'])
        
        # State validation with jurisdiction check
        self._validate_state_jurisdiction(user_data['state'])
        
        # Authority name validation
        self._validate_authority_name(user_data['authority'])
        
        # Information request validation
        self._validate_information_request(user_data['info'], user_data.get('state'))
        
        # Contact validation
        if user_data.get('contact'):
            self._validate_contact(user_data['contact'])
        
        # BPL validation
        if user_data.get('bpl'):
            self._validate_bpl_details(user_data, user_data.get('state'))
        
        # Check for potentially exempt categories
        self._check_section_8_compliance(user_data['info'])
        
        # Date consistency checks (if dates provided)
        if user_data.get('application_date'):
            self._validate_date_consistency(user_data.get('application_date'))
        
        # No blocking issues means validation passed
        return len(self.blocking_issues) == 0 and len(self.errors) == 0
    
    def validate_affidavit(self, user_data):
        """Smart validation for affidavits"""
        self.reset()
        
        # Required fields
        required_fields = ['deponent_name', 'age', 'father_name', 'address', 'statements']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                self.errors.append(f"❌ Missing required field: {field}")
        
        if self.errors:
            return False
        
        # Age validation with guardian requirement check
        age_valid, guardian_needed = self._validate_age_for_affidavit(
            user_data['age'],
            user_data.get('state', 'Maharashtra')
        )
        
        if not age_valid:
            return False
        
        # If guardian needed, check guardian details
        if guardian_needed:
            if not user_data.get('guardian_name'):
                self.blocking_issues.append(
                    "🚫 Deponent is minor (under 18). Guardian details are MANDATORY."
                )
                self.errors.append("Guardian name is required for minor deponents")
            
            if not user_data.get('guardian_age'):
                self.errors.append("Guardian age is required")
            
            if not user_data.get('guardian_father_name'):
                self.errors.append("Guardian's father's name is required")
            
            # Validate guardian is adult
            if user_data.get('guardian_age'):
                try:
                    g_age = int(user_data['guardian_age'])
                    if g_age < 18:
                        self.blocking_issues.append("🚫 Guardian must be at least 18 years old")
                except ValueError:
                    self.errors.append("Guardian age must be a valid number")
        
        # Name validations
        self._validate_name(user_data['deponent_name'], 'Deponent Name')
        self._validate_name(user_data['father_name'], "Father's/Husband's Name")
        
        if guardian_needed and user_data.get('guardian_name'):
            self._validate_name(user_data['guardian_name'], 'Guardian Name')
        
        # Address validation
        self._validate_address(user_data['address'])
        
        # Statements validation
        self._validate_affidavit_statements(user_data['statements'])
        
        # State validation for stamp requirement
        if user_data.get('state'):
            self._validate_state_jurisdiction(user_data['state'])
            self._check_stamp_requirements(user_data['state'])
        
        return len(self.blocking_issues) == 0 and len(self.errors) == 0
    
    def _validate_name(self, name, field_name):
        """Validate name field"""
        if len(name) < 3:
            self.errors.append(f"❌ {field_name} must be at least 3 characters")
        
        if not re.match(r'^[A-Za-z\s\.]+$', name):
            self.warnings.append(f"⚠️  {field_name} contains special characters. Legal documents typically use only letters")
        
        if name.isupper() or name.islower():
            self.suggestions.append(f"💡 Use proper capitalization for {field_name} (e.g., 'Rajesh Kumar')")
    
    def _validate_address(self, address):
        """Validate address completeness"""
        if len(address) < 15:
            self.warnings.append("⚠️  Address seems very short. Provide complete address including house/flat number, street, city, and PIN code")
        
        # Check for PIN code
        if not re.search(r'\b\d{6}\b', address):
            self.warnings.append("⚠️  Address should include 6-digit PIN code")
        
        # Suggest format if too brief
        if len(address) < 30:
            self.suggestions.append("💡 Recommended address format: 'House No., Street/Area, City, State - PIN'")
    
    def _validate_state_jurisdiction(self, state):
        """Validate state and check jurisdiction support"""
        if state not in self.INDIAN_STATES:
            self.errors.append(f"❌ '{state}' is not a valid Indian state/UT")
            self.suggestions.append(f"💡 Did you mean one of: Maharashtra, Karnataka, Delhi, Gujarat, Tamil Nadu?")
            return False
        
        # Check if we have jurisdiction data
        if state not in self.jurisdictions:
            self.warnings.append(f"⚠️  Limited jurisdiction data for {state}. Using default rules")
            self.suggestions.append(f"💡 For best results, use: Maharashtra, Karnataka, Delhi, Gujarat, Tamil Nadu, UP, West Bengal, or Rajasthan")
        
        return True
    
    def _validate_authority_name(self, authority):
        """Validate authority/department name"""
        if len(authority) < 5:
            self.errors.append("❌ Authority/Department name is too short")
        
        # Suggest full names
        if any(abbr in authority for abbr in ['Corp', 'Dept', 'Off']):
            self.suggestions.append("💡 Use full authority name (e.g., 'Municipal Corporation' not 'Muncipal Corp')")
    
    def _validate_information_request(self, info_text, state=None):
        """Validate information request quality"""
        info_length = len(info_text.strip())
        
        if info_length < 30:
            self.warnings.append("⚠️  Information request is very brief. Be more specific for better results")
            self.suggestions.append("💡 Include: specific documents, time periods, file numbers, departments")
        
        if info_length > 3000:
            self.warnings.append("⚠️  Request is very long. Consider breaking into multiple applications")
        
        # Check for specificity markers
        specificity_markers = ['copy of', 'details of', 'list of', 'information regarding']
        if not any(marker in info_text.lower() for marker in specificity_markers):
            self.suggestions.append("💡 Start with specific phrases: 'Copy of...', 'Details of...', 'List of...'")
        
        # Check for time period
        has_time_period = any(keyword in info_text.lower() for keyword in [
            'year', 'month', 'period', 'from', 'to', 'during', '2020', '2021', '2022', '2023', '2024', '2025'
        ])
        
        if not has_time_period:
            self.warnings.append("⚠️  No time period specified. Specify date range for better clarity")
            self.suggestions.append("💡 Example: 'from January 2023 to December 2023' or 'for financial year 2023-24'")
        
        # Check for questions vs document requests
        question_marks = info_text.count('?')
        if question_marks > 2:
            self.warnings.append("⚠️  RTI is for information/documents, not for answering questions")
            self.suggestions.append("💡 Instead of 'Why was X done?', request 'Copy of file noting explaining decision on X'")
    
    def _validate_contact(self, contact):
        """Validate contact information"""
        # Mobile number pattern
        mobile_pattern = r'^[6-9]\d{9}$'
        # Email pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        contact = contact.strip()
        
        is_mobile = re.match(mobile_pattern, contact)
        is_email = re.match(email_pattern, contact)
        
        if not (is_mobile or is_email):
            self.warnings.append("⚠️  Contact should be valid 10-digit mobile (starting with 6-9) or email")
    
    def _validate_bpl_details(self, user_data, state):
        """Validate BPL card details"""
        if not user_data.get('bpl_card_number'):
            self.warnings.append("⚠️  BPL applicants should provide BPL card number for verification")
            self.suggestions.append("💡 Add BPL card number to avoid fee payment issues")
        
        # Check if state offers BPL exemption
        if state and state in self.jurisdictions:
            rti_rules = self.jurisdictions[state]['rti_rules']
            if not rti_rules.get('bpl_exemption'):
                self.warnings.append(f"⚠️  {state} may not offer BPL fee exemption. Verify with local rules")
    
    def _check_section_8_compliance(self, info_text):
        """Check for potentially exempt information categories"""
        if not self.rti_categories:
            return
        
        info_lower = info_text.lower()
        detected_issues = []
        
        # Check auto-detect keywords
        auto_detect = self.rti_categories.get('auto_detect_keywords', {})
        
        for category, keywords in auto_detect.items():
            for keyword in keywords:
                if keyword.lower() in info_lower:
                    cat_info = self.rti_categories['categories'].get(category, {})
                    
                    if cat_info.get('section_8_exempt'):
                        exemption_ref = cat_info.get('exemption_reference', 'Section 8')
                        
                        detected_issues.append({
                            'category': cat_info.get('name', category),
                            'exemption': exemption_ref,
                            'keyword': keyword
                        })
                        
                        # Check if this category blocks generation
                        if cat_info.get('block_generation'):
                            self.blocking_issues.append(
                                f"🚫 Request likely to be REJECTED: {cat_info.get('block_message', 'Highly exempt category')}"
                            )
                    
                    break  # One keyword match per category is enough
        
        # Report detected issues
        if detected_issues:
            self.warnings.append(f"⚠️  Detected {len(detected_issues)} potential exemption(s) under RTI Act:")
            
            for issue in detected_issues:
                self.warnings.append(f"   • {issue['category']} ({issue['exemption']}) - keyword: '{issue['keyword']}'")
            
            self.suggestions.append("💡 Review Section 8 & 9 of RTI Act. Consider narrowing request to non-exempt aspects")
    
    def _validate_date_consistency(self, application_date):
        """Validate date consistency"""
        try:
            app_date = datetime.strptime(application_date, '%Y-%m-%d')
            today = datetime.now()
            
            # Check if date is in future
            if app_date > today:
                self.errors.append("❌ Application date cannot be in the future")
            
            # Check if date is too old
            days_old = (today - app_date).days
            if days_old > 90:
                self.warnings.append(f"⚠️  Application date is {days_old} days old. RTI must be filed within reasonable time")
        
        except ValueError:
            self.errors.append("❌ Invalid date format. Use YYYY-MM-DD")
    
    def _validate_age_for_affidavit(self, age, state):
        """Validate age and determine if guardian is needed"""
        try:
            age_int = int(age)
            
            if age_int < 1 or age_int > 120:
                self.errors.append("❌ Invalid age. Must be between 1 and 120")
                return False, False
            
            # Get jurisdiction rules for guardian age
            guardian_age_limit = 18  # Default
            if state in self.jurisdictions:
                guardian_age_limit = self.jurisdictions[state]['affidavit_rules'].get('guardian_age_limit', 18)
            
            guardian_needed = age_int < guardian_age_limit
            
            if guardian_needed:
                self.warnings.append(f"⚠️  Deponent is minor (age {age_int}). Guardian details are REQUIRED")
                self.suggestions.append("💡 Provide guardian's name, age, and father's name")
            
            return True, guardian_needed
        
        except ValueError:
            self.errors.append("❌ Age must be a valid number")
            return False, False
    
    def _validate_affidavit_statements(self, statements):
        """Validate affidavit statements quality"""
        if not statements or len(statements) == 0:
            self.errors.append("❌ Affidavit must contain at least one statement")
            return
        
        if len(statements) > 30:
            self.warnings.append("⚠️  Affidavit has many statements. Consider creating multiple affidavits if unrelated")
        
        # Validate each statement
        for i, statement in enumerate(statements, 1):
            if not statement.strip():
                self.errors.append(f"❌ Statement {i} is empty")
                continue
            
            if len(statement) < 10:
                self.warnings.append(f"⚠️  Statement {i} is very brief. Be more specific")
            
            # Check for opinion words (affidavits should be factual)
            opinion_words = ['think', 'believe', 'feel', 'probably', 'maybe', 'might', 'could be']
            if any(word in statement.lower() for word in opinion_words):
                self.warnings.append(f"⚠️  Statement {i} contains opinion words. Affidavits should state facts only")
                self.suggestions.append(f"💡 Statement {i}: Replace opinions with factual statements")
            
            # Check for hearsay
            hearsay_indicators = ['i heard', 'someone told', 'it is said', 'people say', 'rumor']
            if any(phrase in statement.lower() for phrase in hearsay_indicators):
                self.warnings.append(f"⚠️  Statement {i} may be based on hearsay. Use direct knowledge only")
            
            # Check if starts with "that"
            if not statement.lower().strip().startswith('that'):
                self.suggestions.append(f"💡 Statement {i}: Should start with 'that' as per legal format")
    
    def _check_stamp_requirements(self, state):
        """Check stamp paper requirements for state"""
        if state in self.jurisdictions:
            affidavit_rules = self.jurisdictions[state]['affidavit_rules']
            
            if affidavit_rules.get('stamp_mandatory'):
                stamp_value = affidavit_rules.get('stamp_paper_value', 0)
                self.suggestions.append(
                    f"💡 {state} requires affidavit on stamp paper of Rs. {stamp_value}/-. "
                    "This will be noted in the generated document"
                )
    
    def get_validation_report(self):
        """Generate comprehensive validation report"""
        report = []
        
        # Blocking issues first (if any)
        if self.blocking_issues:
            report.append("🚫 BLOCKING ISSUES (CANNOT PROCEED):")
            report.append("=" * 60)
            for issue in self.blocking_issues:
                report.append(f"  {issue}")
            report.append("")
        
        # Errors
        if self.errors:
            report.append("❌ ERRORS (Must Fix):")
            report.append("=" * 60)
            for error in self.errors:
                report.append(f"  {error}")
            report.append("")
        
        # Warnings
        if self.warnings:
            report.append("⚠️  WARNINGS (Strongly Recommended):")
            report.append("=" * 60)
            for warning in self.warnings:
                report.append(f"  {warning}")
            report.append("")
        
        # Suggestions
        if self.suggestions:
            report.append("💡 SUGGESTIONS (For Better Results):")
            report.append("=" * 60)
            for suggestion in self.suggestions:
                report.append(f"  {suggestion}")
            report.append("")
        
        # Success message
        if not self.errors and not self.blocking_issues and not self.warnings:
            report.append("✅ All validations passed! Document is ready for generation.")
            report.append("=" * 60)
        
        return "\n".join(report) if report else "✅ Validation complete."
    
    def has_blocking_issues(self):
        """Check if there are issues that block document generation"""
        return len(self.blocking_issues) > 0 or len(self.errors) > 0
    
    def get_complexity_score(self, user_data, doc_type):
        """Calculate complexity score for demonstration purposes"""
        score = {
            'validation_checks': 0,
            'jurisdiction_rules': 0,
            'legal_compliance': 0,
            'smart_features': 0
        }
        
        # Count validation checks performed
        score['validation_checks'] = len(self.errors) + len(self.warnings) + len(self.suggestions)
        
        # Jurisdiction rules applied
        if user_data.get('state') in self.jurisdictions:
            score['jurisdiction_rules'] = 5
        
        # Legal compliance checks
        if doc_type == 'RTI':
            detected_cats = len(self._detect_categories_internal(user_data.get('info', '')))
            score['legal_compliance'] = detected_cats * 3
        
        # Smart features (age check, date validation, etc.)
        score['smart_features'] = 8
        
        total = sum(score.values())
        
        return score, total
    
    def _detect_categories_internal(self, info_text):
        """Internal category detection for scoring"""
        if not self.rti_categories:
            return []
        
        info_lower = info_text.lower()
        detected = []
        
        auto_detect = self.rti_categories.get('auto_detect_keywords', {})
        for category, keywords in auto_detect.items():
            if any(kw.lower() in info_lower for kw in keywords):
                detected.append(category)
        
        return detected
