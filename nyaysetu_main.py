#!/usr/bin/env python3
"""
NyaySetu - Advanced Legal Document Generation System
National Hackathon Edition

Features:
✨ Jurisdiction-aware document generation
✨ Smart legal validation prevents invalid documents
✨ Document lifecycle tracking with automatic deadlines
✨ RTI auto-appeal generation
✨ Explainable AI - shows why clauses were added
✨ Category-based compliance checking
"""

import os
import sys
from datetime import datetime
from document_engine import RTIApplicationGenerator, AffidavitGenerator, JurisdictionManager, DocumentLifecycle
from validation import SmartLegalValidator


class NyaySetuAdvanced:
    """Advanced NyaySetu Application"""
    
    def __init__(self):
        self.validator = SmartLegalValidator()
        self.jurisdiction_mgr = JurisdictionManager()
        self.lifecycle_mgr = DocumentLifecycle()
        self.output_dir = 'generated_documents'
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.user_id = None
    
    def clear_screen(self):
        """Clear terminal"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """Print application header"""
        print("=" * 75)
        print(" " * 22 + "🏛️  NYAYSETU 🏛️")
        print(" " * 12 + "Advanced Legal Document Generation System")
        print(" " * 18 + "National Hackathon Edition")
        print("=" * 75)
        print()
    
    def print_menu(self):
        """Main menu"""
        print("\n📋 MAIN MENU")
        print("=" * 75)
        print("📄 DOCUMENT GENERATION:")
        print("  1. Generate RTI Application (Jurisdiction-Aware)")
        print("  2. Generate Affidavit (State-Specific Format)")
        print()
        print("⚖️  RTI LIFECYCLE MANAGEMENT:")
        print("  3. Generate First Appeal (Auto from Original RTI)")
        print("  4. View Document Lifecycle & Deadlines")
        print("  5. Update Document Status")
        print()
        print("🔍 DOCUMENT INTELLIGENCE:")
        print("  6. View Document Generation Explanation")
        print("  7. Check Legal Compliance (Before Filing)")
        print()
        print("  8. Exit")
        print("=" * 75)
    
    def get_user_session(self):
        """User session"""
        if not self.user_id:
            print("\n🔐 User Authentication")
            print("-" * 75)
            user_id = input("Enter your User ID (or press Enter for new): ").strip()
            if not user_id:
                user_id = f"USER_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                print(f"✅ Created User ID: {user_id}")
            self.user_id = user_id
            print(f"✅ Session: {self.user_id}\n")
    
    def generate_rti(self):
        """Generate advanced RTI application"""
        self.clear_screen()
        self.print_header()
        print("📄 ADVANCED RTI APPLICATION GENERATOR")
        print("=" * 75)
        print("This system:")
        print("  ✓ Validates legal compliance BEFORE generation")
        print("  ✓ Auto-detects Section 8 exemptions")
        print("  ✓ Applies state-specific legal rules")
        print("  ✓ Tracks deadlines automatically")
        print("  ✓ Explains why each clause was added")
        print("=" * 75)
        print()
        
        user_data = {}
        
        # Step 1: Applicant Details
        print("STEP 1: APPLICANT DETAILS")
        print("-" * 75)
        user_data['name'] = input("Full Name (as per ID proof): ").strip()
        user_data['address'] = input("Complete Address (House, Street, City, PIN): ").strip()
        
        # State selection with jurisdiction info
        print("\n📍 Select State/UT:")
        states = list(self.jurisdiction_mgr.profiles.keys())
        for i, state in enumerate(states, 1):
            print(f"  {i}. {state}")
        
        state_input = input("\nEnter number or state name: ").strip()
        if state_input.isdigit() and 1 <= int(state_input) <= len(states):
            user_data['state'] = states[int(state_input) - 1]
        else:
            user_data['state'] = state_input
        
        # Show jurisdiction info
        if user_data['state'] in self.jurisdiction_mgr.profiles:
            jurisdiction = self.jurisdiction_mgr.profiles[user_data['state']]
            rti_rules = jurisdiction['rti_rules']
            print(f"\n✅ Loaded jurisdiction rules for {user_data['state']}:")
            print(f"   • Application Fee: Rs. {rti_rules['fee']}/-")
            print(f"   • Payment Modes: {', '.join(rti_rules['payment_modes'])}")
            print(f"   • BPL Exemption: {'Yes' if rti_rules['bpl_exemption'] else 'No'}")
        
        user_data['contact'] = input("\nMobile Number or Email: ").strip()
        user_data['email'] = input("Email (optional): ").strip()
        
        # Step 2: Authority Details
        print("\n\nSTEP 2: PUBLIC AUTHORITY DETAILS")
        print("-" * 75)
        user_data['authority'] = input("Public Authority/Department Full Name: ").strip()
        user_data['pio_address'] = input("Complete Address of PIO Office: ").strip()
        user_data['reference_number'] = input("Reference Number (if any, optional): ").strip()
        
        # Step 3: Information Request
        print("\n\nSTEP 3: INFORMATION REQUESTED")
        print("-" * 75)
        print("💡 TIP: Be specific! Include:")
        print("   • Exact document names or file numbers")
        print("   • Time period (from X date to Y date)")
        print("   • Department/section if known")
        print()
        print("Enter your information request (Press Enter twice when done):")
        print()
        
        info_lines = []
        empty_count = 0
        while True:
            line = input()
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                info_lines.append(line)
        
        user_data['info'] = "\n".join(info_lines)
        
        # Step 4: Fee Details
        print("\n\nSTEP 4: FEE PAYMENT")
        print("-" * 75)
        bpl_input = input("Do you have a BPL card? (yes/no): ").strip().lower()
        user_data['bpl'] = bpl_input in ['yes', 'y']
        
        if user_data['bpl']:
            user_data['bpl_card_number'] = input("BPL Card Number: ").strip()
        
        # Format preference
        print("\nPreferred information format:")
        print("  1. Electronic (PDF/Digital)")
        print("  2. Physical (Printed copies)")
        print("  3. Both")
        
        format_choice = input("Select (1-3): ").strip()
        format_map = {
            '1': 'electronic',
            '2': 'physical',
            '3': 'electronic and physical'
        }
        user_data['format_preference'] = format_map.get(format_choice, 'electronic/physical')
        
        # VALIDATION PHASE
        print("\n\n" + "=" * 75)
        print("🔍 PHASE 1: SMART LEGAL VALIDATION")
        print("=" * 75)
        
        if not self.validator.validate_rti_application(user_data):
            print("\n" + self.validator.get_validation_report())
            
            if self.validator.has_blocking_issues():
                print("\n🚫 GENERATION BLOCKED: Critical issues must be resolved first.")
                retry = input("\nFix issues and retry? (yes/no): ").strip().lower()
                if retry in ['yes', 'y']:
                    return self.generate_rti()
                else:
                    input("\nPress Enter to return to menu...")
                    return
            else:
                proceed = input("\nWarnings found. Proceed anyway? (yes/no): ").strip().lower()
                if proceed not in ['yes', 'y']:
                    return
        else:
            print("\n✅ Validation passed!")
        
        # Show validation report even if passed
        if self.validator.warnings or self.validator.suggestions:
            print("\n" + self.validator.get_validation_report())
            input("\nPress Enter to continue...")
        
        # COMPLIANCE CHECK PHASE
        print("\n\n" + "=" * 75)
        print("📋 PHASE 2: SECTION 8 COMPLIANCE CHECK")
        print("=" * 75)
        
        detected_categories = self.jurisdiction_mgr.detect_rti_category(user_data['info'])
        
        if detected_categories:
            print(f"\n⚠️  Detected {len(detected_categories)} information category/categories:")
            
            for cat in detected_categories:
                cat_info = self.jurisdiction_mgr.get_category_info(cat)
                print(f"\n• {cat_info.get('name', cat)}")
                
                if cat_info.get('section_8_exempt'):
                    print(f"  ⚠️  Exemption: {cat_info.get('exemption_reference')}")
                    print(f"  ℹ️  {cat_info.get('processing_notes', 'May be partially exempt')}")
                else:
                    print(f"  ✅ Generally not exempt")
            
            print(f"\n💡 These categories will trigger appropriate legal clauses in your application")
            
            modify = input("\nDo you want to modify your request? (yes/no): ").strip().lower()
            if modify in ['yes', 'y']:
                print("\nEnter modified information request (Press Enter twice when done):")
                info_lines = []
                empty_count = 0
                while True:
                    line = input()
                    if line.strip() == "":
                        empty_count += 1
                        if empty_count >= 2:
                            break
                    else:
                        empty_count = 0
                        info_lines.append(line)
                
                user_data['info'] = "\n".join(info_lines)
        else:
            print("\n✅ No Section 8 exemptions detected. Request appears compliant.")
        
        # GENERATION PHASE
        print("\n\n" + "=" * 75)
        print("📄 PHASE 3: DOCUMENT GENERATION")
        print("=" * 75)
        
        generator = RTIApplicationGenerator()
        filename = f"RTI_Application_{user_data['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            print("\n⚙️  Generating jurisdiction-specific RTI application...")
            user_data['application_date'] = datetime.now().strftime('%Y-%m-%d')
            
            doc_hash, deadlines = generator.generate(user_data, output_path)
            
            print(f"\n✅ DOCUMENT GENERATED SUCCESSFULLY!")
            print("=" * 75)
            print(f"📁 Filename: {filename}")
            print(f"📂 Location: {output_path}")
            print(f"📏 Size: {os.path.getsize(output_path)} bytes")
            print(f"🔑 Document Hash: {doc_hash}")
            
            # Show explanation
            print("\n\n" + "=" * 75)
            print("💡 DOCUMENT GENERATION EXPLANATION")
            print("=" * 75)
            print(generator.generate_explanation_report())
            
            # Show deadlines
            if deadlines:
                print("\n\n" + "=" * 75)
                print("⏰ AUTOMATIC DEADLINE TRACKING")
                print("=" * 75)
                print(f"📅 Reply Deadline: {deadlines.get('reply_deadline', 'N/A')[:10]}")
                print(f"   ({deadlines.get('reply_deadline_days', 0)} days from submission)")
                print(f"📅 Appeal Deadline: {deadlines.get('first_appeal_deadline', 'N/A')[:10]}")
                print(f"   ({deadlines.get('first_appeal_days', 0)} days from reply)")
                print(f"\nℹ️  {deadlines.get('description', '')}")
            
            # Save RTI data for potential appeal
            rti_data_file = output_path.replace('.pdf', '_data.json')
            import json
            with open(rti_data_file, 'w') as f:
                json.dump(user_data, f, indent=2)
            
            print("\n\n" + "=" * 75)
            print("📌 NEXT STEPS")
            print("=" * 75)
            print("1. Print the generated PDF")
            print("2. Sign at the designated place")
            print(f"3. Attach fee of Rs. {self.jurisdiction_mgr.get_jurisdiction(user_data['state'])['rti_rules']['fee']}/-")
            print("   (unless BPL exemption applies)")
            print("4. Submit to the Public Information Officer")
            print("5. Keep a copy for your records")
            print()
            print("⏰ Track your deadlines using option 4 in main menu")
            print("📧 If no reply in 30 days, generate First Appeal using option 3")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        input("\n\nPress Enter to return to main menu...")
    
    def generate_affidavit(self):
        """Generate jurisdiction-specific affidavit"""
        self.clear_screen()
        self.print_header()
        print("📜 ADVANCED AFFIDAVIT GENERATOR")
        print("=" * 75)
        print("This system:")
        print("  ✓ Checks age for guardian requirement")
        print("  ✓ Applies state-specific stamp rules")
        print("  ✓ Uses correct court designations")
        print("  ✓ Validates statement quality")
        print("=" * 75)
        print()
        
        user_data = {}
        
        # Step 1: Deponent Details
        print("STEP 1: DEPONENT DETAILS")
        print("-" * 75)
        user_data['deponent_name'] = input("Full Name of Deponent: ").strip()
        user_data['age'] = input("Age: ").strip()
        
        # Check if minor
        try:
            age_int = int(user_data['age'])
            is_minor = age_int < 18
            
            if is_minor:
                print(f"\n⚠️  Deponent is minor (age {age_int}). Guardian details required!")
                print("-" * 75)
                user_data['guardian_name'] = input("Guardian's Full Name: ").strip()
                user_data['guardian_age'] = input("Guardian's Age: ").strip()
                user_data['guardian_father_name'] = input("Guardian's Father's Name: ").strip()
        except:
            pass
        
        user_data['father_name'] = input("Father's/Husband's Name (of Deponent): ").strip()
        user_data['gender'] = input("Gender (male/female): ").strip()
        user_data['address'] = input("Complete Address: ").strip()
        
        # State selection
        print("\n📍 Select State (for stamp paper rules):")
        states = list(self.jurisdiction_mgr.profiles.keys())
        for i, state in enumerate(states, 1):
            print(f"  {i}. {state}")
        
        state_input = input("\nEnter number or state name: ").strip()
        if state_input.isdigit() and 1 <= int(state_input) <= len(states):
            user_data['state'] = states[int(state_input) - 1]
        else:
            user_data['state'] = state_input
        
        # Show stamp requirements
        if user_data['state'] in self.jurisdiction_mgr.profiles:
            jurisdiction = self.jurisdiction_mgr.profiles[user_data['state']]
            affidavit_rules = jurisdiction['affidavit_rules']
            print(f"\n✅ {user_data['state']} Affidavit Rules:")
            print(f"   • Stamp Paper Value: Rs. {affidavit_rules['stamp_paper_value']}/-")
            print(f"   • Notary Required: {'Yes' if affidavit_rules['notary_required'] else 'No'}")
            print(f"   • Court Designation: {affidavit_rules['court_designation']}")
        
        # Step 2: Statements
        print("\n\nSTEP 2: AFFIDAVIT STATEMENTS")
        print("-" * 75)
        print("💡 TIP: Each statement should:")
        print("   • State facts, not opinions")
        print("   • Be based on direct knowledge")
        print("   • Start with 'that' (auto-added if missing)")
        print()
        print("Enter each statement (type 'DONE' when finished):")
        print()
        
        statements = []
        i = 1
        while True:
            statement = input(f"Statement {i}: ").strip()
            if statement.upper() == 'DONE':
                break
            if statement:
                statements.append(statement)
                i += 1
        
        user_data['statements'] = statements
        
        # VALIDATION
        print("\n\n" + "=" * 75)
        print("🔍 SMART LEGAL VALIDATION")
        print("=" * 75)
        
        if not self.validator.validate_affidavit(user_data):
            print("\n" + self.validator.get_validation_report())
            
            if self.validator.has_blocking_issues():
                print("\n🚫 GENERATION BLOCKED: Must fix critical issues.")
                retry = input("\nRetry? (yes/no): ").strip().lower()
                if retry in ['yes', 'y']:
                    return self.generate_affidavit()
                else:
                    input("\nPress Enter to return...")
                    return
            else:
                proceed = input("\nProceed with warnings? (yes/no): ").strip().lower()
                if proceed not in ['yes', 'y']:
                    return
        else:
            print("\n✅ Validation passed!")
        
        # Show suggestions
        if self.validator.suggestions:
            print("\n" + self.validator.get_validation_report())
            input("\nPress Enter to continue...")
        
        # GENERATION
        print("\n\n" + "=" * 75)
        print("📄 DOCUMENT GENERATION")
        print("=" * 75)
        
        generator = AffidavitGenerator()
        filename = f"Affidavit_{user_data['deponent_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            print("\n⚙️  Generating state-specific affidavit...")
            
            doc_hash = generator.generate(user_data, output_path)
            
            print(f"\n✅ AFFIDAVIT GENERATED SUCCESSFULLY!")
            print("=" * 75)
            print(f"📁 Filename: {filename}")
            print(f"📂 Location: {output_path}")
            print(f"🔑 Document Hash: {doc_hash}")
            
            # Show explanation
            print("\n\n" + "=" * 75)
            print("💡 DOCUMENT GENERATION EXPLANATION")
            print("=" * 75)
            print(generator.generate_explanation_report())
            
            # Next steps
            print("\n\n" + "=" * 75)
            print("📌 NEXT STEPS")
            print("=" * 75)
            if user_data['state'] in self.jurisdiction_mgr.profiles:
                stamp_value = self.jurisdiction_mgr.profiles[user_data['state']]['affidavit_rules']['stamp_paper_value']
                print(f"1. Get Non-Judicial Stamp Paper of Rs. {stamp_value}/- from authorized vendor")
            print("2. Print the affidavit on the stamp paper")
            print("3. Sign in front of Notary Public/Oath Commissioner")
            print("4. Get it notarized with seal")
            print("5. Submit as required")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        input("\n\nPress Enter to return to main menu...")
    
    def generate_first_appeal(self):
        """Auto-generate First Appeal from original RTI"""
        self.clear_screen()
        self.print_header()
        print("⚖️  AUTOMATIC FIRST APPEAL GENERATOR")
        print("=" * 75)
        print("Generate First Appeal under Section 19(1) of RTI Act")
        print("Uses data from your original RTI application")
        print("=" * 75)
        print()
        
        # List generated RTI applications
        import glob
        import json
        
        rti_data_files = glob.glob(os.path.join(self.output_dir, 'RTI_Application_*_data.json'))
        
        if not rti_data_files:
            print("❌ No RTI applications found. Generate an RTI first (Option 1)")
            input("\nPress Enter to continue...")
            return
        
        print(f"Found {len(rti_data_files)} RTI application(s):")
        print()
        
        for i, file in enumerate(rti_data_files, 1):
            with open(file, 'r') as f:
                data = json.load(f)
            print(f"{i}. {data['name']} - {data['authority']}")
            print(f"   Date: {data.get('application_date', 'N/A')}")
        
        selection = input("\nSelect RTI number for appeal: ").strip()
        
        try:
            idx = int(selection) - 1
            with open(rti_data_files[idx], 'r') as f:
                original_rti = json.load(f)
        except:
            print("Invalid selection")
            input("Press Enter...")
            return
        
        # Reason for appeal
        print("\n\nSelect reason for appeal:")
        print("1. No reply received within 30 days")
        print("2. Incomplete information provided")
        print("3. Information denied wrongly")
        print("4. Excessive fee demanded")
        print("5. Other (custom reason)")
        
        reason_choice = input("\nSelect (1-5): ").strip()
        
        reason_map = {
            '1': 'I have not received any response within the statutory period of 30 days',
            '2': 'the information provided is incomplete and does not address my specific queries',
            '3': 'the information has been wrongly denied citing exemptions that do not apply',
            '4': 'excessive fee has been demanded without proper justification',
            '5': ''
        }
        
        appeal_reason = reason_map.get(reason_choice, reason_map['1'])
        
        if reason_choice == '5':
            appeal_reason = input("\nEnter custom reason: ").strip()
        
        # Generate appeal
        print("\n\n" + "=" * 75)
        print("📄 GENERATING FIRST APPEAL")
        print("=" * 75)
        
        generator = RTIApplicationGenerator()
        filename = f"RTI_First_Appeal_{original_rti['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        try:
            print("\n⚙️  Auto-generating First Appeal from original RTI data...")
            
            doc_hash = generator.generate_first_appeal(original_rti, appeal_reason, output_path)
            
            print(f"\n✅ FIRST APPEAL GENERATED!")
            print("=" * 75)
            print(f"📁 Filename: {filename}")
            print(f"📂 Location: {output_path}")
            print(f"🔑 Hash: {doc_hash}")
            
            print("\n\n" + "=" * 75)
            print("📌 NEXT STEPS")
            print("=" * 75)
            print("1. Print the generated First Appeal")
            print("2. Sign at designated place")
            print("3. Attach appeal fee (Rs. 50/- typically)")
            print("4. Submit to First Appellate Authority")
            print("5. Keep acknowledgment")
            print()
            print("⏰ Appeal should be decided within 30 days")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        input("\n\nPress Enter to return...")
    
    def view_lifecycles(self):
        """View document lifecycles and pending deadlines"""
        self.clear_screen()
        self.print_header()
        print("⏰ DOCUMENT LIFECYCLE & DEADLINE TRACKER")
        print("=" * 75)
        
        pending_deadlines = self.lifecycle_mgr.get_pending_deadlines()
        
        if not pending_deadlines:
            print("\n✅ No pending deadlines")
        else:
            print(f"\n📅 You have {len(pending_deadlines)} pending deadline(s):\n")
            
            for deadline in pending_deadlines:
                urgency = "🔴 URGENT" if deadline['is_urgent'] else "🟢"
                print(f"{urgency} {deadline['doc_type']}")
                print(f"   Hash: {deadline['doc_hash'][:32]}...")
                print(f"   Deadline: {deadline['deadline_date'][:10]}")
                print(f"   Days Remaining: {deadline['days_remaining']}")
                print()
        
        input("\nPress Enter to return...")
    
    def update_document_status(self):
        """Update document lifecycle status"""
        self.clear_screen()
        self.print_header()
        print("📝 UPDATE DOCUMENT STATUS")
        print("=" * 75)
        
        # Show active documents
        if not self.lifecycle_mgr.lifecycles:
            print("\n❌ No documents in lifecycle tracker")
            input("Press Enter...")
            return
        
        print("\nActive Documents:")
        docs = list(self.lifecycle_mgr.lifecycles.items())
        
        for i, (doc_hash, lifecycle) in enumerate(docs, 1):
            print(f"\n{i}. {lifecycle['document_type']}")
            print(f"   Hash: {doc_hash[:32]}...")
            print(f"   Status: {lifecycle['current_state']}")
            print(f"   Created: {lifecycle['created_date'][:10]}")
        
        selection = input("\nSelect document number: ").strip()
        
        try:
            idx = int(selection) - 1
            doc_hash, lifecycle = docs[idx]
        except:
            print("Invalid selection")
            input("Press Enter...")
            return
        
        # New status
        print("\n\nAvailable States:")
        states = list(DocumentLifecycle.STATES.keys())
        for i, state in enumerate(states, 1):
            print(f"{i}. {state} - {DocumentLifecycle.STATES[state]}")
        
        state_sel = input("\nSelect new state: ").strip()
        
        try:
            new_state = states[int(state_sel) - 1]
            notes = input("Notes (optional): ").strip()
            
            self.lifecycle_mgr.update_state(doc_hash, new_state, notes)
            print(f"\n✅ Status updated to: {new_state}")
        except:
            print("Invalid selection")
        
        input("\nPress Enter...")
    
    def view_explanation(self):
        """View explanation for last generated document"""
        self.clear_screen()
        self.print_header()
        print("💡 DOCUMENT GENERATION EXPLANATION")
        print("=" * 75)
        print("\nThis feature shows WHY each clause was added to your document.")
        print("It demonstrates the 'Explainable AI' aspect of NyaySetu.")
        print()
        print("(Generate a document first to see explanations)")
        
        input("\n\nPress Enter...")
    
    def check_compliance(self):
        """Pre-filing compliance check"""
        self.clear_screen()
        self.print_header()
        print("🔍 LEGAL COMPLIANCE CHECKER")
        print("=" * 75)
        print("Check RTI application for Section 8 exemptions BEFORE filing")
        print()
        
        info = input("Paste your information request:\n\n")
        
        if not info.strip():
            print("\n❌ No text entered")
            input("Press Enter...")
            return
        
        detected = self.jurisdiction_mgr.detect_rti_category(info)
        
        if not detected:
            print("\n✅ No obvious Section 8 exemptions detected")
            print("Your request appears compliant!")
        else:
            print(f"\n⚠️  Detected {len(detected)} potential issue(s):\n")
            
            for cat in detected:
                cat_info = self.jurisdiction_mgr.get_category_info(cat)
                print(f"• {cat_info.get('name', cat)}")
                if cat_info.get('section_8_exempt'):
                    print(f"  Exemption: {cat_info.get('exemption_reference')}")
                    print(f"  Note: {cat_info.get('processing_notes', '')}")
                print()
        
        input("\nPress Enter...")
    
    def run(self):
        """Main loop"""
        self.clear_screen()
        self.print_header()
        self.get_user_session()
        
        while True:
            self.print_menu()
            
            choice = input("\nEnter choice (1-8): ").strip()
            
            if choice == '1':
                self.generate_rti()
            elif choice == '2':
                self.generate_affidavit()
            elif choice == '3':
                self.generate_first_appeal()
            elif choice == '4':
                self.view_lifecycles()
            elif choice == '5':
                self.update_document_status()
            elif choice == '6':
                self.view_explanation()
            elif choice == '7':
                self.check_compliance()
            elif choice == '8':
                print("\n👋 Thank you for using NyaySetu!")
                print("=" * 75)
                break
            else:
                print("\n❌ Invalid choice")
                input("Press Enter...")


if __name__ == "__main__":
    try:
        app = NyaySetuAdvanced()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Terminated")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
