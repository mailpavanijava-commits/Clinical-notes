"""
Medication Parser Module
Extracts medication information from clinical notes.
"""

import re



class MedicationParser:
    """Parses medication information from clinical text."""
    
    # Common medication patterns
    DOSE_PATTERN = r'(\d+\.?\d*)\s*(mg|mcg|g|ml|units?)'
    FREQUENCY_PATTERNS = {
        
        'twice daily': ['bid', 'twice daily', 'twice a day', '2x daily'],
        'three times daily': ['tid', 'three times daily', '3x daily'],
        'four times daily': ['qid', 'four times daily', '4x daily'],
        'as needed': ['prn', 'as needed', 'as required'],
        'at bedtime': ['hs', 'at bedtime', 'at night', 'qhs']
    }
    
    ROUTE_PATTERNS = {
        
        'intravenous': ['iv', 'intravenous', 'intravenously'],     
        'intravenous': ['iv', 'intravenous', 'intravenously'],
        'intramuscular': ['im', 'intramuscular'],
        'subcutaneous': ['sc', 'subq', 'subcutaneous'],
        'topical': ['topical', 'topically', 'apply']
    }
    
    # Negation patterns for clinical text
    NEGATION_PATTERNS = [
        
        'negative for ', 'none ', 'never ', 'stopped ',
        'discontinued ', 'allergic to '
    ]
    
    # Common medication names (simplified list)
    KNOWN_MEDICATIONS = [
        'metformin', 'lisinopril', 'amlodipine', 'omeprazole',
        'atorvastatin', 'simvastatin', 'levothyroxine', 'metoprolol',
        'losartan', 'gabapentin', 'hydrochlorothiazide', 'furosemide',
        'aspirin', 'ibuprofen', 'acetaminophen', 'prednisone',
        'amoxicillin', 'azithromycin', 'ciprofloxacin', 'insulin'
    ]
    
    def __init__(self):
        """Initialize the medication parser."""
        self.medications = []
    
    def extract_dose(self, text: str) -> Optional[Dict[str, str]]:
        """
        Extract dosage information from text.
        
        Args:
            text: Clinical text containing dosage
            
        Returns:
            Dictionary with value and unit, or None if not found
        """
        text_lower = text.lower()
        match = re.search(self.DOSE_PATTERN, text_lower)
        
        if match:
            return {
                'value': match.group(1),
                'unit': match.group(2)
            }
        return None
    
    def extract_frequency(self, text: str) -> Optional[str]:
        """
        Extract frequency information from text.
        
        Args:
            text: Clinical text containing frequency
            
        Returns:
            Standardized frequency string, or None if not found
        """
        text_lower = text.lower()
        
        # Check patterns in order of specificity (longer/more specific first)
        # This prevents "daily" from matching before "twice daily"
        check_order = [
            'four times daily',
            'three times daily', 
            'twice daily',
            'at bedtime',
            'as needed',
            'daily'
        ]
        
        for freq_key in check_order:
            patterns = self.FREQUENCY_PATTERNS[freq_key]
            for pattern in patterns:
                if pattern in text_lower:
                    return freq_key
        return None
    
    def extract_route(self, text: str) -> Optional[str]:
        """
        Extract route of administration from text.
        
        Args:
            text: Clinical text containing route
            
        Returns:
            Standardized route string, or None if not found
        """
        text_lower = text.lower()
        
        for standard_route, patterns in self.ROUTE_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return standard_route
        return None
    
    def find_medications(self, text: str) -> List[str]:
        """
        Find known medication names in text.
        
        Args:
            text: Clinical text to search
            
        Returns:
            List of medication names found
        """
        text_lower = text.lower()
        found = []
        
        for med in self.KNOWN_MEDICATIONS:
            if med in text_lower:
                found.append(med)
        
        return found
    
    def is_negated(self, text: str, medication: str) -> bool:
        """
        Check if a medication mention is negated.
        
        Args:
            text: Clinical text
            medication: Medication name to check
            
        Returns:
            True if the medication is negated, False otherwise
        """
        text_lower = text.lower()
        med_lower = medication.lower()
        
        # Find position of medication in text
        med_pos = text_lower.find(med_lower)
        if med_pos == -1:
            return False
        
        # Check if any negation pattern appears before the medication
        # within a reasonable window (50 characters)
        window_start = max(0, med_pos - 50)
        text_before = text_lower[window_start:med_pos]
        
        for neg_pattern in self.NEGATION_PATTERNS:
            if neg_pattern in text_before:
                return True
        
        return False
    
    def parse(self, text: str) -> List[Dict]:
        """
        Parse clinical text and extract all medication information.
        
        Args:
            text: Clinical note text
            
        Returns:
            List of medication dictionaries
        """
        medications = []
        found_meds = self.find_medications(text)
        
        # For each medication found, try to extract details
        for med_name in found_meds:
            medication = {
                'name': med_name,
                'dose': self.extract_dose(text),
                'frequency': self.extract_frequency(text),
                'route': self.extract_route(text)
            }
            medications.append(medication)
        
        self.medications = medications
        return medications
    
    def get_summary(self) -> str:
        """
        Get a human-readable summary of parsed medications.
        
        Returns:
            Summary string
        """
        if not self.medications:
            return "No medications found."
        
        lines = []
        for med in self.medications:
            parts = [med['name'].capitalize()]
            
            if med['dose']:
                parts.append(f"{med['dose']['value']}{med['dose']['unit']}")
            if med['route']:
                parts.append(med['route'])
            if med['frequency']:
                parts.append(med['frequency'])
            
            lines.append(' '.join(parts))
        
        return '\n'.join(lines)


def main():
    """Example usage of MedicationParser."""
    sample_note = """
    Patient is a 55 y/o male with Type 2 Diabetes and Hypertension.
    Current medications:
    - Metformin 500mg PO twice daily
    - Lisinopril 10mg oral daily
    - Aspirin 81mg by mouth daily
    """
    
    parser = MedicationParser()
    results = parser.parse(sample_note)
    
    print("Parsed Medications:")
    print("-" * 40)
    print(parser.get_summary())
    print("-" * 40)
    print(f"Total medications found: {len(results)}")


if __name__ == "__main__":
    main()
