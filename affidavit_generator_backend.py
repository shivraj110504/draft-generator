"""
Affidavit Generator Module - Production Ready
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import json
import hashlib
import os


class AffidavitGenerator:
    """Production-ready affidavit generator"""
    
    def __init__(self):
        self.styles = self._setup_styles()
        # Keep outputs local to the backend directory
        self.output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _setup_styles(self):
        """Setup affidavit styles"""
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            name="AffTitle",
            parent=styles["Title"],
            fontSize=16,
            fontName="Times-Bold",
            alignment=TA_CENTER,
            spaceAfter=15,
            underline=True
        ))
        
        styles.add(ParagraphStyle(
            name="AffBody",
            parent=styles["Normal"],
            fontSize=12,
            fontName="Times-Roman",
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=18
        ))
        
        return styles
    
    def _generate_hash(self, data):
        """Generate document hash"""
        content_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    def generate(self, user_data):
        """
        Generate Affidavit PDF
        
        Args:
            user_data (dict): Affidavit details
            
        Returns:
            dict: {pdf_file, document_hash}
        """
        doc_hash = self._generate_hash(user_data)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        filename = f"Affidavit_{user_data['deponent_name'].replace(' ', '_')}_{timestamp}.pdf"
        file_path = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=1*inch
        )
        
        story = []
        
        # Court header if applicable
        if user_data.get('court_name'):
            story.append(Paragraph(
                f"IN THE {user_data['court_name'].upper()}",
                self.styles["AffTitle"]
            ))
            story.append(Spacer(1, 10))
            
            if user_data.get('case_number'):
                story.append(Paragraph(
                    f"Case No: {user_data['case_number']}",
                    self.styles["Heading2"]
                ))
                story.append(Spacer(1, 15))
        
        # Title
        story.append(Paragraph("AFFIDAVIT", self.styles["AffTitle"]))
        story.append(Spacer(1, 20))
        
        # Deponent info
        gender = user_data.get('gender', 'male').lower()
        relation = 'son' if gender == 'male' else 'daughter'
        
        story.append(Paragraph(
            f"I, <b>{user_data['deponent_name']}</b>, "
            f"{relation} of <b>{user_data.get('father_name', '_____________')}</b>, "
            f"aged about <b>{user_data.get('age', '_____')}</b> years, "
            f"residing at <b>{user_data['address']}</b>, "
            f"do hereby solemnly affirm and state as under:",
            self.styles["AffBody"]
        ))
        story.append(Spacer(1, 20))
        
        # Statements
        statements = user_data.get('statements', [])
        for i, statement in enumerate(statements, 1):
            story.append(Paragraph(
                f"<b>{i}.</b> {statement}",
                self.styles["AffBody"]
            ))
            story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 30))
        
        # Deponent signature
        story.append(Paragraph("DEPONENT", self.styles["AffTitle"]))
        story.append(Spacer(1, 40))
        story.append(Paragraph("_________________________", self.styles["Normal"]))
        story.append(Paragraph(f"({user_data['deponent_name']})", self.styles["Normal"]))
        story.append(Spacer(1, 40))
        
        # Verification
        story.append(Paragraph("VERIFICATION", self.styles["AffTitle"]))
        story.append(Spacer(1, 15))
        
        verification = f"""I, <b>{user_data['deponent_name']}</b>, the deponent above named, 
do hereby verify that the contents of the above affidavit are true and correct to the best 
of my knowledge and belief and nothing material has been concealed therefrom."""
        story.append(Paragraph(verification, self.styles["AffBody"]))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph(
            f"Verified at <b>{user_data.get('place', '_______________')}</b> "
            f"on this <b>{datetime.now().strftime('%d day of %B, %Y')}</b>.",
            self.styles["AffBody"]
        ))
        story.append(Spacer(1, 40))
        
        story.append(Paragraph("DEPONENT", self.styles["AffTitle"]))
        story.append(Spacer(1, 40))
        story.append(Paragraph("_________________________", self.styles["Normal"]))
        story.append(Paragraph(f"({user_data['deponent_name']})", self.styles["Normal"]))
        
        # Build PDF
        doc.build(story)
        
        return {
            'pdf_file': file_path,
            'document_hash': doc_hash
        }
