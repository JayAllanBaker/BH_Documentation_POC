from sqlalchemy import or_, and_, not_
from models import Patient, Document, Condition
import re

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
                # Search across all searchable fields
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

def search_patients(query):
    """Search patients using HTQL query"""
    parser = HTQLParser()
    filter_condition = parser.build_filter(query)
    if filter_condition is not None:
        return Patient.query.filter(filter_condition).all()
    return Patient.query.all()

def search_documents(query):
    """Search documents using HTQL query"""
    parser = HTQLParser()
    filter_condition = parser.build_filter(query)
    if filter_condition is not None:
        return Document.query.filter(filter_condition).all()
    return Document.query.all()
