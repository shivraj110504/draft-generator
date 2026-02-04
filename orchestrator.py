"""
Document Orchestrator - AI-powered requirement analysis
"""

import re


class DocumentOrchestrator:
    """Orchestrates multi-document generation with AI analysis"""
    
    TEMPLATES = {
        "RTI_APPLICATION": {
            "name": "RTI Application",
            "complexity": 8,
            "keywords": ["rti", "information", "government", "records", "public"]
        },
        "AFFIDAVIT": {
            "name": "Affidavit",
            "complexity": 7,
            "keywords": ["affidavit", "sworn", "court", "declare", "verify"]
        }
    }
    
    def analyze_requirements(self, description):
        """
        Analyze user requirement and suggest document type
        
        Args:
            description (str): User's natural language description
            
        Returns:
            dict: Analysis with document type, complexity, suggestions
        """
        desc_lower = description.lower()
        
        # Detect document type
        primary_doc = None
        max_matches = 0
        
        for doc_type, info in self.TEMPLATES.items():
            matches = sum(1 for kw in info['keywords'] if kw in desc_lower)
            if matches > max_matches:
                max_matches = matches
                primary_doc = doc_type
        
        if not primary_doc:
            primary_doc = "RTI_APPLICATION"  # Default
        
        template_info = self.TEMPLATES[primary_doc]
        
        # Calculate complexity
        complexity_score = template_info['complexity'] * 10
        complexity_score += 15  # AI validation
        complexity_score += 10  # Blockchain
        
        # Detect challenges
        challenges = []
        if any(word in desc_lower for word in ['urgent', 'emergency', 'immediate']):
            challenges.append("Urgent request - ensure timeline is mentioned")
        
        if any(word in desc_lower for word in ['court', 'legal', 'case']):
            challenges.append("Legal matter - ensure all legal requirements are met")
        
        return {
            'primary_document': primary_doc,
            'document_name': template_info['name'],
            'estimated_complexity': template_info['complexity'],
            'complexity_score': complexity_score,
            'estimated_time_minutes': 15,
            'potential_challenges': challenges,
            'recommended_approach': f"Generate {template_info['name']} with legal validation"
        }
    
    def calculate_complexity_score(self, document_data):
        """
        Calculate complexity score for a document
        
        Args:
            document_data (dict): Document configuration
            
        Returns:
            dict: Complexity breakdown
        """
        score = 0
        factors = []
        
        # Base from template
        doc_type = document_data.get('type', 'RTI_APPLICATION')
        template = self.TEMPLATES.get(doc_type, self.TEMPLATES['RTI_APPLICATION'])
        base_score = template['complexity'] * 10
        score += base_score
        factors.append(f"Template base: {base_score}")
        
        # Validation
        if document_data.get('validation_enabled', True):
            score += 15
            factors.append("AI validation: +15")
        
        # Blockchain
        if document_data.get('blockchain_enabled', True):
            score += 10
            factors.append("Blockchain: +10")
        
        # Citations
        if document_data.get('citations', True):
            score += 10
            factors.append("Legal citations: +10")
        
        return {
            'total_score': score,
            'breakdown': factors,
            'level': 'HIGH' if score > 70 else 'MEDIUM' if score > 40 else 'LOW'
        }
