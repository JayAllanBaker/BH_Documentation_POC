from sqlalchemy import or_, and_, not_
from models import Patient, Document, Condition, ICD10Code
import re
import json
import os
from functools import lru_cache
from flask import current_app

class HTQLParser:
    def __init__(self):
        self.operators = {
            'AND': and_,
            'OR': or_,
            'NOT': not_
        }
        
        self.field_mappings = {
            'patient': {
                'name': lambda v: or_(
                    Patient.family_name.ilike(f'%{v}%'),
                    Patient.given_name.ilike(f'%{v}%')
                ),
                'id': lambda v: Patient.identifier == v,
                'gender': lambda v: Patient.gender.ilike(f'%{v}%'),
                'city': lambda v: Patient.city.ilike(f'%{v}%'),
                'state': lambda v: Patient.state.ilike(f'%{v}%')
            },
            'document': {
                'title': lambda v: Document.title.ilike(f'%{v}%'),
                'content': lambda v: Document.content.ilike(f'%{v}%'),
                'transcription': lambda v: Document.transcription.ilike(f'%{v}%')
            },
            'condition': {
                'code': lambda v: Condition.code.ilike(f'%{v}%'),
                'status': lambda v: Condition.clinical_status.ilike(f'%{v}%'),
                'severity': lambda v: Condition.severity.ilike(f'%{v}%')
            }
        }

    def tokenize(self, query):
        """Split query into tokens, preserving quoted strings"""
        pattern = r'(?:[^\s"]+|"[^"]*")+|AND|OR|NOT'
        return [token.strip('"') for token in re.findall(pattern, query)]

    def parse_field(self, field_expr):
        """Parse field expressions like field:value or field.subfield:value"""
        if ':' not in field_expr:
            return None, field_expr
            
        field, value = field_expr.split(':', 1)
        field_parts = field.split('.')
        return field_parts, value.strip('"')

    def build_filter(self, query):
        """Build SQLAlchemy filter from HTQL query"""
        tokens = self.tokenize(query)
        filters = []
        current_operator = 'AND'
        negate_next = False
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if token in self.operators:
                current_operator = token
                i += 1
                continue
                
            if token == 'NOT':
                negate_next = True
                i += 1
                continue
            
            field_parts, value = self.parse_field(token)
            
            if field_parts:
                main_field, *sub_fields = field_parts
                if main_field in self.field_mappings:
                    field_mapping = self.field_mappings[main_field]
                    sub_field = sub_fields[0] if sub_fields else 'name'
                    
                    if sub_field in field_mapping:
                        condition = field_mapping[sub_field](value)
                        if negate_next:
                            condition = not_(condition)
                            negate_next = False
                            
                        if filters and current_operator in self.operators:
                            filters = [self.operators[current_operator](filters[0], condition)]
                        else:
                            filters = [condition]
            else:
                conditions = []
                for field_type in self.field_mappings.values():
                    for field_func in field_type.values():
                        conditions.append(field_func(value))
                
                combined = or_(*conditions)
                if negate_next:
                    combined = not_(combined)
                    negate_next = False
                    
                if filters and current_operator in self.operators:
                    filters = [self.operators[current_operator](filters[0], combined)]
                else:
                    filters = [combined]
            
            i += 1
            
        return filters[0] if filters else None

@lru_cache(maxsize=1)
def load_medical_codes():
    """Load ICD-10 and SNOMED CT codes from JSON files"""
    codes = {
        'ICD-10': {
            'E11': 'Type 2 diabetes mellitus',
            'E11.0': 'Type 2 diabetes with hyperosmolarity',
            'E11.1': 'Type 2 diabetes with ketoacidosis',
            'E11.2': 'Type 2 diabetes with kidney complications',
            'E11.21': 'Type 2 diabetes with diabetic nephropathy',
            'E11.22': 'Type 2 diabetes with diabetic chronic kidney disease',
            'E11.3': 'Type 2 diabetes with ophthalmic complications',
            'E11.31': 'Type 2 diabetes with background retinopathy',
            'E11.32': 'Type 2 diabetes with proliferative retinopathy',
            'E11.4': 'Type 2 diabetes with neurological complications',
            'E11.40': 'Type 2 diabetes with diabetic neuropathy, unspecified',
            'E11.41': 'Type 2 diabetes with diabetic mononeuropathy',
            'E11.42': 'Type 2 diabetes with diabetic polyneuropathy',
            'E11.43': 'Type 2 diabetes with diabetic autonomic (poly)neuropathy',
            'E11.5': 'Type 2 diabetes with circulatory complications',
            'E11.51': 'Type 2 diabetes with diabetic peripheral angiopathy without gangrene',
            'E11.52': 'Type 2 diabetes with diabetic peripheral angiopathy with gangrene',
            'E11.6': 'Type 2 diabetes with other specified complications',
            'E11.8': 'Type 2 diabetes with unspecified complications',
            'E11.9': 'Type 2 diabetes without complications',
            'I10': 'Essential (primary) hypertension',
            'I11': 'Hypertensive heart disease',
            'I11.0': 'Hypertensive heart disease with heart failure',
            'I11.9': 'Hypertensive heart disease without heart failure',
            'J45': 'Asthma',
            'J45.0': 'Predominantly allergic asthma',
            'J45.1': 'Nonallergic asthma',
            'J45.2': 'Mixed asthma',
            'J45.3': 'Severe persistent asthma',
            'J45.4': 'Mild intermittent asthma',
            'J45.5': 'Mild persistent asthma',
            'J45.9': 'Other and unspecified asthma',
            'F32': 'Major depressive disorder, single episode',
            'F32.0': 'Major depressive disorder, single episode, mild',
            'F32.1': 'Major depressive disorder, single episode, moderate',
            'F32.2': 'Major depressive disorder, single episode, severe without psychotic features',
            'F32.3': 'Major depressive disorder, single episode, severe with psychotic features',
            'F32.4': 'Major depressive disorder, single episode, in partial remission',
            'F32.5': 'Major depressive disorder, single episode, in full remission',
            'F41': 'Other anxiety disorders',
            'F41.0': 'Panic disorder without agoraphobia',
            'F41.1': 'Generalized anxiety disorder',
            'F41.2': 'Mixed anxiety and depressive disorder',
            'F41.3': 'Other mixed anxiety disorders',
            'F41.8': 'Other specified anxiety disorders',
            'F41.9': 'Anxiety disorder, unspecified'
        },
        'SNOMED-CT': {
            '44054006': 'Type 2 diabetes mellitus (disorder)',
            '38341003': 'Hypertensive disorder, systemic arterial (disorder)',
            '195967001': 'Asthma (disorder)',
            '370143000': 'Major depression, single episode (disorder)',
            '197480006': 'Anxiety disorder (disorder)',
            '371631005': 'Panic disorder (disorder)',
            '73211009': 'Diabetes mellitus (disorder)',
            '59621000': 'Essential hypertension (disorder)',
            '35489007': 'Depressive disorder (disorder)',
            '69479009': 'Allergic asthma (disorder)',
            '46635009': 'Type 1 diabetes mellitus (disorder)',
            '422034002': 'Diabetic retinopathy (disorder)',
            '421920002': 'Diabetic peripheral neuropathy (disorder)',
            '421893009': 'Diabetic renal disease (disorder)',
            '197591003': 'Generalized anxiety disorder (disorder)',
            '191736004': 'Chronic depression (disorder)',
            '191747006': 'Seasonal affective disorder (disorder)',
            '191659001': 'Atopic asthma (disorder)',
            '195977004': 'Asthma with status asthmaticus (disorder)',
            '195978009': 'Mild asthma (disorder)'
        }
    }
    return codes

def get_code_suggestions(prefix, code_type=None):
    """Get medical code suggestions based on prefix"""
    try:
        current_app.logger.debug(f'Getting code suggestions for prefix: {prefix}, type: {code_type}')
        suggestions = []
        seen_codes = set()  # Track seen codes to avoid duplicates
        
        # Search the database for ICD-10 codes first
        if not code_type or code_type.upper() == 'ICD-10':
            db_suggestions = ICD10Code.search_codes(prefix)
            for code in db_suggestions:
                if code.code not in seen_codes:
                    suggestions.append({
                        'code': code.code,
                        'description': code.description,
                        'system': 'ICD-10'
                    })
                    seen_codes.add(code.code)
        
        # Then add hardcoded codes if they're not already included
        codes = load_medical_codes()
        if code_type and code_type.upper() in codes:
            add_suggestions(code_type.upper(), codes[code_type.upper()], suggestions, seen_codes)
        else:
            for system, system_codes in codes.items():
                add_suggestions(system, system_codes, suggestions, seen_codes)
        
        # Sort suggestions by relevance
        suggestions.sort(key=lambda x: get_sort_key(x, prefix))
        return suggestions[:10]  # Limit to top 10 suggestions
        
    except Exception as e:
        current_app.logger.error(f'Error getting code suggestions: {str(e)}')
        return []

def add_suggestions(code_system, codes_dict, suggestions, seen_codes):
    """Helper function to add suggestions while avoiding duplicates"""
    for code, desc in codes_dict.items():
        if code not in seen_codes and (
            code.lower().startswith(prefix.lower()) or 
            desc.lower().find(prefix.lower()) != -1
        ):
            suggestions.append({
                'code': code,
                'description': desc,
                'system': code_system
            })
            seen_codes.add(code)

def get_sort_key(suggestion, prefix):
    """Get sort key for suggestion relevance"""
    code = suggestion['code'].lower()
    desc = suggestion['description'].lower()
    prefix_lower = prefix.lower()
    
    if code == prefix_lower:
        return (0, code)
    elif code.startswith(prefix_lower):
        return (1, code)
    elif desc.startswith(prefix_lower):
        return (2, code)
    else:
        return (3, code)

def search_patients(query):
    """Search patients using HTQL query"""
    try:
        current_app.logger.debug(f'Searching patients with query: {query}')
        parser = HTQLParser()
        filter_condition = parser.build_filter(query)
        if filter_condition is not None:
            return Patient.query.join(
                Condition, 
                Patient.id == Condition.patient_id, 
                isouter=True
            ).filter(filter_condition).distinct().all()
        return Patient.query.all()
    except Exception as e:
        current_app.logger.error(f'Error searching patients: {str(e)}')
        return []

def search_documents(query):
    """Search documents using HTQL query"""
    try:
        current_app.logger.debug(f'Searching documents with query: {query}')
        parser = HTQLParser()
        filter_condition = parser.build_filter(query)
        if filter_condition is not None:
            return Document.query.join(
                Patient, 
                Document.patient_id == Patient.id,
                isouter=True
            ).join(
                Condition,
                Patient.id == Condition.patient_id,
                isouter=True
            ).filter(filter_condition).distinct().all()
        return Document.query.all()
    except Exception as e:
        current_app.logger.error(f'Error searching documents: {str(e)}')
        return []