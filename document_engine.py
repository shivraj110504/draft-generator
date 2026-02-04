"""
NyaySetu - Advanced Legal Document Generation Engine
Features:
- Jurisdiction-aware document variants
- Smart legal validation
- Document lifecycle tracking
- Explainable clause generation
- Auto-appeal generation for RTI
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from datetime import datetime, timedelta
import json
import hashlib
import os
import re


from database import NyaySetuDB

class JurisdictionManager:
    """Manages jurisdiction-specific legal requirements and formats"""
    
    def __init__(self):
        self.load_profiles()
        self.load_categories()
    
    def load_profiles(self):
        """Load jurisdiction profiles"""
        # Ensure path is local to the module
        profiles_path = os.path.join(os.path.dirname(__file__), 'jurisdiction_profiles.json')
        with open(profiles_path, 'r') as f:
            self.profiles = json.load(f)
    
    def load_categories(self):
        """Load RTI categories and compliance rules"""
        # Ensure path is local to the module
        categories_path = os.path.join(os.path.dirname(__file__), 'rti_categories.json')
        with open(categories_path, 'r') as f:
            self.category_data = json.load(f)

    def get_jurisdiction(self, state):
        """Get jurisdiction profile for state"""
        return self.profiles.get(state, self.profiles['Maharashtra'])
    
    def detect_rti_category(self, info_text):
        """Auto-detect RTI information category from request text"""
        info_lower = info_text.lower()
        detected_categories = []
        
        # Check against keywords
        for category, keywords in self.category_data['auto_detect_keywords'].items():
            for keyword in keywords:
                if keyword.lower() in info_lower:
                    detected_categories.append(category)
                    break
        
        return list(set(detected_categories))  # Remove duplicates
    
    def get_category_info(self, category_key):
        """Get full category information"""
        return self.category_data['categories'].get(category_key, {})
    
    def get_additional_clause(self, clause_key):
        """Get additional clause text"""
        return self.category_data['additional_clauses_library'].get(clause_key, {})

class DocumentLifecycle:
    """Tracks document lifecycle and manages deadlines using MongoDB"""
    
    STATES = {
        'DRAFTED': 'Document has been generated',
        'SUBMITTED': 'Document submitted to authority',
        'ACKNOWLEDGED': 'Receipt acknowledged by authority',
        'REPLY_RECEIVED': 'Response received from authority',
        'APPEAL_FILED': 'First appeal filed',
        'CLOSED': 'Matter resolved/closed'
    }
    
    def __init__(self):
        self.db = NyaySetuDB()
        # Fallback to local dict if DB unavailable
        self.lifecycles = self.db.get_lifecycles() if self.db.client is not None else {}
    
    def create_lifecycle(self, doc_hash, doc_type, metadata):
        """Create new document lifecycle"""
        # Calculate deadlines based on document type
        deadlines = self._calculate_deadlines(doc_type, metadata)
        
        if self.db.client is not None:
            self.db.save_lifecycle(doc_hash, doc_type, metadata, deadlines)
            self.lifecycles = self.db.get_lifecycles()
        else:
            # Fallback local storage (legacy)
            self.lifecycles[doc_hash] = {
                'document_type': doc_type,
                'created_date': datetime.now().isoformat(),
                'current_state': 'DRAFTED',
                'state_history': [
                    {
                        'state': 'DRAFTED',
                        'timestamp': datetime.now().isoformat(),
                        'notes': 'Document generated'
                    }
                ],
                'metadata': metadata,
                'deadlines': deadlines
            }
        
        return deadlines
    
    def _calculate_deadlines(self, doc_type, metadata):
        """Calculate important deadlines for document"""
        deadlines = {}
        
        if doc_type == 'RTI_Application':
            # RTI Act mandates 30 days response
            submission_date = datetime.now()
            reply_deadline = submission_date + timedelta(days=30)
            appeal_deadline = submission_date + timedelta(days=60)  # 30 days from reply deadline
            
            deadlines = {
                'reply_deadline': reply_deadline.isoformat(),
                'reply_deadline_days': 30,
                'first_appeal_deadline': appeal_deadline.isoformat(),
                'first_appeal_days': 30,
                'description': 'RTI Act 2005 mandates response within 30 days of receipt'
            }
        
        elif doc_type == 'Legal_Notice':
            notice_period = metadata.get('notice_period_days', 15)
            notice_deadline = datetime.now() + timedelta(days=notice_period)
            
            deadlines = {
                'response_deadline': notice_deadline.isoformat(),
                'response_deadline_days': notice_period,
                'description': f'Recipient must respond within {notice_period} days'
            }
        
        return deadlines
    
    def update_state(self, doc_hash, new_state, notes=''):
        """Update document lifecycle state"""
        if doc_hash not in self.lifecycles:
            return False
        
        lifecycle = self.lifecycles[doc_hash]
        lifecycle['current_state'] = new_state
        lifecycle['state_history'].append({
            'state': new_state,
            'timestamp': datetime.now().isoformat(),
            'notes': notes
        })
        
        self._save_lifecycles()
        return True
    
    def get_pending_deadlines(self):
        """Get all pending deadlines across documents"""
        pending = []
        now = datetime.now()
        
        for doc_hash, lifecycle in self.lifecycles.items():
            if lifecycle['current_state'] in ['DRAFTED', 'SUBMITTED', 'ACKNOWLEDGED']:
                deadlines = lifecycle['deadlines']
                
                for deadline_key, deadline_iso in deadlines.items():
                    if deadline_key.endswith('_deadline') and isinstance(deadline_iso, str):
                        try:
                            deadline_date = datetime.fromisoformat(deadline_iso)
                            days_remaining = (deadline_date - now).days
                            
                            if days_remaining >= 0:
                                pending.append({
                                    'doc_hash': doc_hash,
                                    'doc_type': lifecycle['document_type'],
                                    'deadline_type': deadline_key,
                                    'deadline_date': deadline_iso,
                                    'days_remaining': days_remaining,
                                    'is_urgent': days_remaining <= 7
                                })
                        except:
                            pass
        
        return sorted(pending, key=lambda x: x['days_remaining'])


class AdvancedDocumentEngine:
    """Base class for advanced document generation"""
    
    def __init__(self):
        self.styles = self._setup_styles()
        self.jurisdiction_mgr = JurisdictionManager()
        self.lifecycle_mgr = DocumentLifecycle()
        self.document_hash = None
        self.explanation_log = []  # Track why clauses were added
    
    def _setup_styles(self):
        """Setup professional legal document styles"""
        styles = getSampleStyleSheet()
        
        # Title - Bold, Centered
        styles.add(ParagraphStyle(
            name='DocTitle',
            parent=styles['Heading1'],
            fontSize=13,
            textColor=colors.black,
            spaceAfter=24,
            spaceBefore=12,
            alignment=TA_CENTER,
            fontName='Times-Bold',
            leading=16
        ))
        
        # Subject line
        styles.add(ParagraphStyle(
            name='Subject',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=14,
            spaceBefore=10,
            alignment=TA_LEFT,
            fontName='Times-Bold',
            leading=14
        ))
        
        # Body Text - Justified, exactly as legal documents
        styles.add(ParagraphStyle(
            name='BodyJustify',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            leading=15,
            spaceBefore=6,
            spaceAfter=6,
            firstLineIndent=0
        ))
        
        # Right Aligned
        styles.add(ParagraphStyle(
            name='RightAlign',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT,
            fontName='Times-Roman',
            leading=14
        ))
        
        return styles
    
    def log_clause_explanation(self, clause_type, reason, legal_ref=''):
        """Log explanation for why a clause was added"""
        self.explanation_log.append({
            'clause_type': clause_type,
            'reason': reason,
            'legal_reference': legal_ref,
            'timestamp': datetime.now().isoformat()
        })
    
    def generate_explanation_report(self):
        """Generate human-readable explanation of document generation"""
        if not self.explanation_log:
            return "Standard document generated without additional clauses."
        
        report = ["Document Generation Explanation:", "=" * 50]
        
        for i, entry in enumerate(self.explanation_log, 1):
            report.append(f"\n{i}. {entry['clause_type']}")
            report.append(f"   Reason: {entry['reason']}")
            if entry['legal_reference']:
                report.append(f"   Legal Basis: {entry['legal_reference']}")
        
        return "\n".join(report)


class RTIApplicationGenerator(AdvancedDocumentEngine):
    """Advanced RTI Application Generator with jurisdiction awareness"""
    
    def generate(self, user_data, output_path):
        """Generate jurisdiction-specific RTI application"""
        
        # Get jurisdiction profile
        state = user_data['state']
        jurisdiction = self.jurisdiction_mgr.get_jurisdiction(state)
        rti_rules = jurisdiction['rti_rules']
        
        # Detect information category
        detected_categories = self.jurisdiction_mgr.detect_rti_category(user_data['info'])
        
        # Setup document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=2.5*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm,
            title=f"RTI Application - {user_data['name']}"
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            "APPLICATION UNDER THE RIGHT TO INFORMATION ACT, 2005",
            self.styles['DocTitle']
        ))
        story.append(Spacer(1, 0.4*inch))
        
        # To Address
        pio_designation = rti_rules['pio_designation']
        to_address = f"""
        <b>To,</b><br/>
        The {pio_designation},<br/>
        {user_data['authority']},<br/>
        {user_data['pio_address']}
        """
        story.append(Paragraph(to_address, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.3*inch))
        
        # Reference number (if provided)
        if user_data.get('reference_number'):
            story.append(Paragraph(
                f"<b>Ref No.:</b> {user_data['reference_number']}",
                self.styles['BodyJustify']
            ))
            story.append(Spacer(1, 0.15*inch))
        
        # Subject - make it specific, not generic
        subject_text = self._generate_specific_subject(user_data['info'])
        story.append(Paragraph(
            f"<b>Subject:</b> {subject_text}",
            self.styles['Subject']
        ))
        story.append(Spacer(1, 0.25*inch))
        
        # Salutation
        story.append(Paragraph("Respected Sir/Madam,", self.styles['BodyJustify']))
        story.append(Spacer(1, 0.2*inch))
        
        # Main Body - varied based on context
        intro_text = self._generate_contextual_intro(user_data, jurisdiction)
        story.append(Paragraph(intro_text, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.2*inch))
        
        # Information Requested Section
        story.append(Paragraph(
            "<b>INFORMATION SOUGHT:</b>",
            self.styles['Subject']
        ))
        story.append(Spacer(1, 0.1*inch))
        
        # Format information requests professionally
        info_paragraphs = self._format_information_requests(user_data['info'])
        for para in info_paragraphs:
            story.append(Paragraph(para, self.styles['BodyJustify']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.15*inch))
        
        # Add category-specific clauses
        if detected_categories:
            category_clauses = self._add_category_clauses(detected_categories, story)
        
        # Fee Payment Clause - jurisdiction specific
        fee_text = self._generate_fee_clause(user_data, rti_rules)
        story.append(Paragraph(fee_text, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.15*inch))
        
        self.log_clause_explanation(
            'Fee Clause',
            f'State-specific fee rules applied for {state}',
            f'{state} RTI Rules'
        )
        
        # Format preference
        format_pref = user_data.get('format_preference', 'electronic/physical')
        story.append(Paragraph(
            f"I request that the information be provided in <b>{format_pref}</b> format as per my convenience.",
            self.styles['BodyJustify']
        ))
        story.append(Spacer(1, 0.15*inch))
        
        # Severability clause (Section 10)
        story.append(Paragraph(
            "If any portion of the requested information is exempt from disclosure, I request that the remaining non-exempt portions be provided separately as per Section 10 of the RTI Act, 2005.",
            self.styles['BodyJustify']
        ))
        story.append(Spacer(1, 0.15*inch))
        
        self.log_clause_explanation(
            'Severability Clause',
            'Added to ensure partial information is disclosed even if some parts are exempt',
            'Section 10, RTI Act 2005'
        )
        
        # Declaration
        story.append(Paragraph(
            "I hereby declare that the information sought does not fall within the restricted categories under Sections 8 and 9 of the RTI Act, 2005, to the best of my knowledge and belief.",
            self.styles['BodyJustify']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Closing
        story.append(Paragraph("Thanking you,", self.styles['BodyJustify']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Yours faithfully,", self.styles['BodyJustify']))
        story.append(Spacer(1, 0.6*inch))
        
        # Signature Block - proper table layout
        sig_date = datetime.now().strftime('%d/%m/%Y')
        signature_data = [
            ["Place: _____________________", ""],
            [f"Date: {sig_date}", ""],
            ["", ""],
            ["", "(Signature of Applicant)"],
            ["", ""],
            [f"<b>Name:</b> {user_data['name']}", ""],
            [f"<b>Address:</b> {user_data['address']}", ""],
        ]
        
        if user_data.get('contact'):
            signature_data.append([f"<b>Contact:</b> {user_data['contact']}", ""])
        
        if user_data.get('email'):
            signature_data.append([f"<b>Email:</b> {user_data['email']}", ""])
        
        sig_table = Table(signature_data, colWidths=[3.2*inch, 2.8*inch])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 11),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 3), (1, 3), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(sig_table)
        
        # Build PDF
        doc.build(story)
        
        # Generate hash and lifecycle
        with open(output_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Create lifecycle tracking
        metadata = {
            'applicant_name': user_data['name'],
            'authority': user_data['authority'],
            'state': state,
            'detected_categories': detected_categories,
            'jurisdiction': state
        }
        
        deadlines = self.lifecycle_mgr.create_lifecycle(file_hash, 'RTI_Application', metadata)
        
        return file_hash, deadlines
    
    def _generate_specific_subject(self, info_text):
        """Generate specific subject line instead of generic one"""
        # Extract key topic from first 100 chars
        preview = info_text[:100].strip()
        
        # Try to extract main topic
        if 'copy' in preview.lower():
            return "Request for certified copies under RTI Act, 2005"
        elif 'details' in preview.lower() or 'information' in preview.lower():
            return "Application seeking information under Section 6(1) of RTI Act, 2005"
        elif 'list' in preview.lower():
            return "Request for list/details under Right to Information Act, 2005"
        else:
            return "Application for information under Section 6(1) of RTI Act, 2005"
    
    def _generate_contextual_intro(self, user_data, jurisdiction):
        """Generate context-appropriate introduction"""
        state = user_data['state']
        
        intro_variants = [
            f"I, <b>{user_data['name']}</b>, a citizen of India residing at <b>{user_data['address']}</b>, hereby submit this application under Section 6(1) of the Right to Information Act, 2005, seeking information from your esteemed office as detailed below:",
            
            f"Respectfully, I, <b>{user_data['name']}</b>, permanent resident of <b>{user_data['address']}</b>, do hereby make this application under the provisions of the Right to Information Act, 2005, requesting the following information which is under the control of your office:",
            
            f"I, <b>{user_data['name']}</b>, residing at <b>{user_data['address']}</b>, submit this application in exercise of my right under Section 6 of the Right to Information Act, 2005, requesting disclosure of the following information:"
        ]
        
        # Use hash of name to consistently pick same variant for same person
        variant_index = hash(user_data['name']) % len(intro_variants)
        return intro_variants[variant_index]
    
    def _format_information_requests(self, info_text):
        """Format information requests into numbered professional paragraphs"""
        # Split by newlines or periods
        raw_requests = [s.strip() for s in info_text.replace('\n', '. ').split('.') if s.strip()]
        
        formatted = []
        for i, request in enumerate(raw_requests, 1):
            # Clean up the request
            request = request.strip()
            if not request:
                continue
            
            # Ensure it starts with lowercase (after number)
            if request[0].isupper() and i > 1:
                request = request[0].lower() + request[1:]
            
            formatted.append(f"{i}. {request.capitalize() if i == 1 else request};")
        
        # Make last one end with period
        if formatted:
            formatted[-1] = formatted[-1].rstrip(';') + '.'
        
        return formatted
    
    def _add_category_clauses(self, categories, story):
        """Add category-specific clauses and warnings"""
        for category in categories:
            cat_info = self.jurisdiction_mgr.get_category_info(category)
            
            if not cat_info:
                continue
            
            # Add warnings as separate paragraph
            if cat_info.get('warnings'):
                story.append(Spacer(1, 0.15*inch))
                warning_text = "<b>Note:</b> " + cat_info['warnings'][0]
                story.append(Paragraph(warning_text, self.styles['BodyJustify']))
                
                self.log_clause_explanation(
                    f'{cat_info["name"]} Warning',
                    f'Auto-detected category: {category}',
                    cat_info.get('exemption_reference', '')
                )
            
            # Add mandatory clauses
            if cat_info.get('additional_clauses'):
                for clause_key in cat_info['additional_clauses']:
                    clause_data = self.jurisdiction_mgr.get_additional_clause(clause_key)
                    if clause_data:
                        story.append(Spacer(1, 0.15*inch))
                        story.append(Paragraph(clause_data['text'], self.styles['BodyJustify']))
                        
                        self.log_clause_explanation(
                            clause_key,
                            f'Required for {cat_info["name"]} requests',
                            clause_data.get('legal_reference', '')
                        )
    
    def _generate_fee_clause(self, user_data, rti_rules):
        """Generate jurisdiction-specific fee clause"""
        if user_data.get('bpl') and rti_rules.get('bpl_exemption'):
            clause = f"""Being a holder of Below Poverty Line (BPL) card, I am exempted from payment of the application fee as per the provisions of the RTI Act, 2005. My BPL Card Number is <b>{user_data.get('bpl_card_number', '[To be provided]')}</b>."""
        else:
            fee = rti_rules['fee']
            payment_modes = ' / '.join(rti_rules['payment_modes'])
            clause = f"""I am submitting the prescribed application fee of <b>Rs. {fee}/-</b> (Rupees {self._amount_in_words(fee)} only) through {payment_modes} as per the RTI Rules applicable in {user_data['state']}."""
        
        return clause
    
    def _amount_in_words(self, amount):
        """Convert amount to words"""
        words = {
            10: "Ten", 20: "Twenty", 30: "Thirty", 50: "Fifty",
            100: "One Hundred", 200: "Two Hundred", 500: "Five Hundred"
        }
        return words.get(amount, str(amount))
    
    def generate_first_appeal(self, original_rti_data, appeal_reason, output_path):
        """Auto-generate First Appeal using original RTI data"""
        state = original_rti_data['state']
        jurisdiction = self.jurisdiction_mgr.get_jurisdiction(state)
        rti_rules = jurisdiction['rti_rules']
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=2.5*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm,
            title=f"RTI First Appeal - {original_rti_data['name']}"
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            "FIRST APPEAL UNDER SECTION 19(1) OF THE RIGHT TO INFORMATION ACT, 2005",
            self.styles['DocTitle']
        ))
        story.append(Spacer(1, 0.4*inch))
        
        # To Address - First Appellate Authority
        appellate_designation = rti_rules['appellate_designation']
        to_address = f"""
        <b>To,</b><br/>
        The {appellate_designation},<br/>
        {original_rti_data['authority']},<br/>
        {original_rti_data['pio_address']}
        """
        story.append(Paragraph(to_address, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.3*inch))
        
        # Subject
        story.append(Paragraph(
            "<b>Subject:</b> First Appeal under Section 19(1) of the RTI Act, 2005 against the decision/non-decision of the Public Information Officer",
            self.styles['Subject']
        ))
        story.append(Spacer(1, 0.25*inch))
        
        # Appeal content
        story.append(Paragraph("Respected Sir/Madam,", self.styles['BodyJustify']))
        story.append(Spacer(1, 0.2*inch))
        
        appeal_intro = f"""I, <b>{original_rti_data['name']}</b>, had filed an RTI application dated <b>{original_rti_data.get('application_date', '____')}</b> with the Public Information Officer of your office. The application sought specific information as detailed below. However, {appeal_reason}. Therefore, I am filing this First Appeal under Section 19(1) of the RTI Act, 2005."""
        
        story.append(Paragraph(appeal_intro, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.2*inch))
        
        # Original information requested
        story.append(Paragraph("<b>ORIGINAL INFORMATION REQUESTED:</b>", self.styles['Subject']))
        story.append(Spacer(1, 0.1*inch))
        
        info_paragraphs = self._format_information_requests(original_rti_data['info'])
        for para in info_paragraphs:
            story.append(Paragraph(para, self.styles['BodyJustify']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Grounds of appeal
        story.append(Paragraph("<b>GROUNDS OF APPEAL:</b>", self.styles['Subject']))
        story.append(Spacer(1, 0.1*inch))
        
        grounds = [
            "The Public Information Officer has failed to provide information within the stipulated period of 30 days as mandated under Section 7(1) of the RTI Act, 2005.",
            "The information requested is not exempt under any provisions of Section 8 or Section 9 of the Act.",
            "The delay/refusal has caused undue hardship and is contrary to the spirit of transparency enshrined in the RTI Act, 2005."
        ]
        
        for i, ground in enumerate(grounds, 1):
            story.append(Paragraph(f"{i}. {ground}", self.styles['BodyJustify']))
            story.append(Spacer(1, 0.08*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Prayer
        story.append(Paragraph("<b>PRAYER:</b>", self.styles['Subject']))
        story.append(Spacer(1, 0.1*inch))
        
        prayer = """In light of the above, I humbly pray that this Hon'ble Appellate Authority may be pleased to direct the Public Information Officer to provide the requested information at the earliest and impose appropriate penalties for the delay as per Section 20 of the RTI Act, 2005."""
        
        story.append(Paragraph(prayer, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.3*inch))
        
        # Closing
        story.append(Paragraph("Thanking you,", self.styles['BodyJustify']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("Yours faithfully,", self.styles['BodyJustify']))
        story.append(Spacer(1, 0.6*inch))
        
        # Signature block
        sig_date = datetime.now().strftime('%d/%m/%Y')
        signature_data = [
            ["Place: _____________________", ""],
            [f"Date: {sig_date}", ""],
            ["", ""],
            ["", "(Signature of Appellant)"],
            ["", ""],
            [f"<b>Name:</b> {original_rti_data['name']}", ""],
            [f"<b>Address:</b> {original_rti_data['address']}", ""],
        ]
        
        if original_rti_data.get('contact'):
            signature_data.append([f"<b>Contact:</b> {original_rti_data['contact']}", ""])
        
        sig_table = Table(signature_data, colWidths=[3.2*inch, 2.8*inch])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Times-Roman', 11),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 3), (1, 3), 'CENTER'),
        ]))
        
        story.append(sig_table)
        
        # Build PDF
        doc.build(story)
        
        with open(output_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        return file_hash


class AffidavitGenerator(AdvancedDocumentEngine):
    """Generate jurisdiction-specific affidavits"""
    
    def generate(self, user_data, output_path):
        """Generate affidavit with jurisdiction-specific formats"""
        
        state = user_data.get('state', 'Maharashtra')
        jurisdiction = self.jurisdiction_mgr.get_jurisdiction(state)
        affidavit_rules = jurisdiction['affidavit_rules']
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=2.5*cm,
            topMargin=3*cm,
            bottomMargin=2.5*cm,
            title=f"Affidavit - {user_data['deponent_name']}"
        )
        
        story = []
        
        # Stamp paper note if required
        if affidavit_rules['stamp_mandatory']:
            stamp_note = f"""<font size=9><i>To be executed on Non-Judicial Stamp Paper of Rs. {affidavit_rules['stamp_paper_value']}/- as per {state} Stamp Act</i></font>"""
            story.append(Paragraph(stamp_note, self.styles['BodyJustify']))
            story.append(Spacer(1, 0.3*inch))
            
            self.log_clause_explanation(
                'Stamp Paper Requirement',
                f'{state} requires stamp paper of Rs. {affidavit_rules["stamp_paper_value"]}',
                f'{state} Stamp Act'
            )
        
        # Title
        story.append(Paragraph("AFFIDAVIT", self.styles['DocTitle']))
        story.append(Spacer(1, 0.3*inch))
        
        # Deponent details - check for minor/guardian requirement
        age = int(user_data['age'])
        guardian_required = age < affidavit_rules['guardian_age_limit']
        
        if guardian_required:
            deponent_intro = f"""I, <b>{user_data['guardian_name']}</b>, aged <b>{user_data['guardian_age']} years</b>, son/daughter/wife of <b>{user_data['guardian_father_name']}</b>, resident of <b>{user_data['address']}</b>, being the lawful guardian of <b>{user_data['deponent_name']}</b>, a minor aged <b>{age} years</b>, do hereby solemnly affirm and state on oath as under:"""
            
            self.log_clause_explanation(
                'Guardian Declaration',
                f'Deponent is minor (age {age}), guardian declaration added as per {state} law',
                f'{state} Majority Act / Indian Contract Act'
            )
        else:
            # Relation determination
            relation = self._determine_relation(user_data.get('gender', 'male'))
            deponent_intro = f"""I, <b>{user_data['deponent_name']}</b>, aged <b>{age} years</b>, {relation} <b>{user_data['father_name']}</b>, resident of <b>{user_data['address']}</b>, do hereby solemnly affirm and state on oath as under:"""
        
        story.append(Paragraph(deponent_intro, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.25*inch))
        
        # Statements
        statements = user_data['statements']
        for i, statement in enumerate(statements, 1):
            # Ensure statement starts with "that"
            if not statement.lower().strip().startswith('that'):
                statement = f"that {statement}"
            
            story.append(Paragraph(f"<b>{i}.</b> {statement.capitalize()};", self.styles['BodyJustify']))
            story.append(Spacer(1, 0.12*inch))
        
        # Make last statement end with period
        story.append(Spacer(1, 0.2*inch))
        
        # Verification clause - format varies by state
        verification_format = affidavit_rules['verification_format']
        
        if verification_format == 'magistrate_court':
            verification = f"""I, the above-named deponent, do hereby verify and state on solemn affirmation that the contents of paragraphs 1 to {len(statements)} stated hereinabove are true and correct to the best of my knowledge and belief, and nothing material has been concealed therefrom. I further state that no part of this affidavit is false and nothing has been concealed herein."""
        else:  # notary_format
            verification = f"""Verified at _____________ on this _____ day of _____________ {datetime.now().year}. I, the deponent above-named, do hereby verify that the contents of this affidavit are true to the best of my knowledge and belief."""
        
        story.append(Paragraph(verification, self.styles['BodyJustify']))
        story.append(Spacer(1, 0.4*inch))
        
        # Deponent signature
        story.append(Paragraph("DEPONENT", self.styles['RightAlign']))
        story.append(Spacer(1, 1*inch))
        
        # Notary/Oath Commissioner section - state specific
        court_designation = affidavit_rules['court_designation']
        
        story.append(Paragraph(
            f"<b>VERIFICATION BY {court_designation.upper()}/NOTARY PUBLIC/OATH COMMISSIONER</b>",
            self.styles['Subject']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        if affidavit_rules.get('witness_required'):
            witness_text = "Identified by me / Identified by _________________________ (Witness Name & Address)"
            self.log_clause_explanation(
                'Witness Requirement',
                f'{state} requires witness identification for affidavits',
                f'{state} Court Rules'
            )
        else:
            witness_text = "Identified by me"
        
        notary_block = f"""
        {witness_text}<br/>
        <br/>
        <b>Signature:</b> _____________________<br/>
        <b>Name:</b> _________________________<br/>
        <b>Designation:</b> {court_designation}/Notary Public/Oath Commissioner<br/>
        <b>Registration No.:</b> ______________<br/>
        <b>Seal:</b><br/>
        <br/>
        <br/>
        """
        
        story.append(Paragraph(notary_block, self.styles['BodyJustify']))
        
        # Build PDF
        doc.build(story)
        
        with open(output_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Create lifecycle
        metadata = {
            'deponent_name': user_data['deponent_name'],
            'state': state,
            'stamp_value': affidavit_rules['stamp_paper_value'],
            'guardian_required': guardian_required
        }
        
        self.lifecycle_mgr.create_lifecycle(file_hash, 'Affidavit', metadata)
        
        return file_hash
    
    def _determine_relation(self, gender):
        """Determine relation descriptor based on gender"""
        gender = gender.lower()
        if gender == 'female':
            return "daughter/wife of"
        else:
            return "son of"
