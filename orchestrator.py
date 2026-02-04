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
            # Comprehensive RTI keywords covering all common scenarios
            "keywords": [
                # Core RTI terms
                "rti", "right to information", "information act", "rti act", "rti application",
                # Government/Public authority terms
                "government", "public authority", "government department", "ministry", "municipality",
                "panchayat", "public sector", "government office", "public office",
                # Information request terms
                "information", "records", "documents", "data", "files", "copies",
                "seeking information", "requesting information", "need information",
                # Specific document types often requested via RTI
                "marksheet", "mark sheet", "answer sheet", "exam records", "exam papers",
                "certificates", "transcripts", "academic records", "educational records",
                "salary records", "pension records", "service records", "government file",
                # RTI-specific terms
                "pio", "public information officer", "cpio", "first appellate authority",
                "section 6", "rti fee", "rti rules", "disclosure",
                # Action terms specific to RTI
                "access to information", "transparency", "accountability",
                "public records", "official documents", "government information",
                # University/Institution scenarios (common RTI use case)
                "university", "college", "exam", "admission", "degree", "diploma",
                "enrollment", "registration", "marks", "grades", "results",
                # Employment/Service scenarios
                "employment records", "appointment letter", "service book", "pay slip",
                # Infrastructure/Development 
                "tender", "contract", "project", "scheme", "subsidy", "allocation",
                # Common phrases
                "want to know", "need details about", "obtain copy",
                "public authority records", "under rti", "using rti"
            ],
            "negative_keywords": ["court", "attorney", "lawyer", "judge", "lawsuit", "litigation"]
        },
        "AFFIDAVIT": {
            "name": "Affidavit",
            "complexity": 7,
            # Comprehensive Affidavit keywords
            "keywords": [
                # Core affidavit terms
                "affidavit", "sworn statement", "oath", "swear", "affirm", "depose",
                "declaration", "notarize", "notary", "attestation",
                # Legal/Court terms
                "court", "legal", "case", "lawsuit", "litigation", "proceedings",
                "tribunal", "hearing", "judge", "magistrate", "attorney", "lawyer",
                "legal proceedings", "court case", "legal matter",
                # Purpose-specific terms
                "testimony", "evidence", "witness", "deponent", "affiant",
                "statement of facts", "sworn testimony", "legal document",
                # Common affidavit scenarios
                "name change", "address proof", "identity proof", "relationship proof",
                "income affidavit", "self declaration", "undertaking", "bond",
                "surety", "indemnity", "guarantee",
                # Court-related scenarios
                "criminal case", "civil case", "family court", "divorce", "custody",
                "property dispute", "inheritance", "will", "succession",
                # Administrative scenarios requiring affidavits
                "passport", "visa", "immigration", "marriage certificate",
                "birth certificate", "death certificate", "legal heir",
                # Action terms specific to affidavits
                "submit to court", "file in court", "legal proof", "sworn before",
                "legally binding statement", "under oath", "penalty of perjury",
                # Verification terms
                "verify", "verification", "certified", "authentic", "genuine",
                "true and correct", "solemnly declare"
            ],
            "negative_keywords": ["government information", "rti", "pio", "public authority"]
        }
    }
    
    # Clarification questions for uncertain cases
    CLARIFICATION_QUESTIONS = [
        {
            "question": "What is the main purpose of your document?",
            "options": [
                {
                    "text": "I need information/records from a government department or public authority",
                    "leads_to": "RTI_APPLICATION",
                    "confidence_boost": 40
                },
                {
                    "text": "I need to make a sworn statement for legal/court purposes",
                    "leads_to": "AFFIDAVIT",
                    "confidence_boost": 40
                },
                {
                    "text": "I need to verify facts or identity for official purposes",
                    "leads_to": "AFFIDAVIT",
                    "confidence_boost": 30
                }
            ]
        }
    ]
    
    def analyze_requirements(self, description):
        """
        Analyze user requirement and suggest document type with confidence scoring
        
        Args:
            description (str): User's natural language description
            
        Returns:
            dict: Analysis with document type, confidence, and optional clarification
        """
        desc_lower = description.lower()
        
        # Calculate scores for each document type
        scores = {}
        for doc_type, info in self.TEMPLATES.items():
            # Positive keyword matches
            positive_matches = sum(1 for kw in info['keywords'] if kw in desc_lower)
            
            # Negative keyword penalties
            negative_matches = sum(1 for kw in info.get('negative_keywords', []) if kw in desc_lower)
            
            # Calculate weighted score
            score = (positive_matches * 10) - (negative_matches * 15)
            scores[doc_type] = max(0, score)  # Ensure non-negative
        
        # Determine primary document
        if not any(scores.values()):
            # No matches at all - need clarification
            return self._generate_clarification_response(0)
        
        primary_doc = max(scores, key=scores.get)
        max_score = scores[primary_doc]
        
        # Calculate confidence (0-100)
        # Confidence is high if there's a clear winner
        second_highest = sorted(scores.values())[-2] if len(scores) > 1 else 0
        score_gap = max_score - second_highest
        
        # Base confidence on score and gap
        if max_score >= 30 and score_gap >= 15:
            confidence = 95
        elif max_score >= 20 and score_gap >= 10:
            confidence = 85
        elif max_score >= 15 and score_gap >= 5:
            confidence = 75
        elif max_score >= 10:
            confidence = 60
        else:
            confidence = 40
        
        # If confidence is low, request clarification
        if confidence < 70:
            return self._generate_clarification_response(confidence, primary_doc)
        
        # High confidence - return recommendation
        template_info = self.TEMPLATES[primary_doc]
        
        # Calculate complexity
        complexity_score = template_info['complexity'] * 10
        complexity_score += 15  # AI validation
        complexity_score += 10  # Blockchain
        
        # Detect challenges
        challenges = []
        if any(word in desc_lower for word in ['urgent', 'emergency', 'immediate']):
            challenges.append("Urgent request - ensure timeline compliance")
        
        if any(word in desc_lower for word in ['court', 'legal', 'case']) and primary_doc == 'RTI_APPLICATION':
            challenges.append("Legal matter - verify if RTI is appropriate or if Affidavit is needed")
        
        # Generate contextual approach
        if primary_doc == "RTI_APPLICATION":
            approach = "Submit RTI application to the Public Information Officer (PIO) of the relevant authority. Include specific details of information needed, payment proof, and contact details."
        else:
            approach = "Prepare sworn affidavit with clear statement of facts. Get it notarized before submitting to the concerned authority or court."
        
        return {
            'status': 'success',
            'primary_document': primary_doc,
            'document_name': template_info['name'],
            'confidence': confidence,
            'estimated_complexity': template_info['complexity'],
            'complexity_score': complexity_score,
            'estimated_time_minutes': 15,
            'potential_challenges': challenges,
            'recommended_approach': approach,
            'score_details': scores  # For debugging
        }
    
    def _generate_clarification_response(self, base_confidence, suggested_doc=None):
        """Generate response requesting clarification from user"""
        return {
            'status': 'needs_clarification',
            'confidence': base_confidence,
            'suggested_document': suggested_doc,
            'questions': self.CLARIFICATION_QUESTIONS,
            'message': 'I need a bit more information to suggest the right document for you.'
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
