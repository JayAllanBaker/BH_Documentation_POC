# Clinical Documentation System

## Overview

An AI-powered behavioral health clinical documentation system designed to generate MEAT (Monitor, Evaluate, Assess, Treat) and TAMPER (Time, Action, Medical Necessity, Plan, Education, Response) compliant medical documentation. The system processes patient visits through audio/video capture, transcription, and automated analysis to create personalized treatment plans and clinical notes.

**Core Purpose**: Reduce documentation burden on healthcare providers while improving treatment plan personalization and regulatory compliance for behavioral health practices.

**Key Capabilities**:
- Multi-modal patient data capture (audio, video, text)
- AI-powered transcription and clinical analysis
- MEAT/TAMPER compliant documentation generation
- Clinical assessment tools (COWS, PRAPARE)
- Patient and condition management
- FHIR-compatible data structures

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: Bootstrap 5.3 with vanilla JavaScript
- Server-side rendered templates using Jinja2
- Progressive enhancement approach with JavaScript modules
- WebRTC for audio/video capture
- Real-time status indicators and progress tracking

**Key Design Patterns**:
- Component-based JavaScript classes (AudioRecorder, HTQLSuggestions)
- Form-centric user interactions with inline validation
- AJAX calls for background processing without page reloads
- Responsive mobile-first design using Bootstrap grid system

### Backend Architecture

**Framework**: Flask (Python) with Blueprint-based modular routing
- RESTful API endpoints for audio processing and document management
- Server-side session management with Flask-Login
- SQLAlchemy ORM for database abstraction
- Alembic for database migrations

**Modular Route Structure**:
- `auth`: Authentication and user management
- `patients`: Patient CRUD and assessments
- `documents`: Clinical documentation with MEAT criteria
- `conditions`: FHIR Condition resource management
- `admin`: System administration and audit logs
- `search`: Advanced HTQL-based search functionality

**AI Integration Pattern**:
- OpenAI GPT-4 for clinical note analysis and MEAT categorization
- Whisper (via external library) for audio transcription
- Modular AI analysis utilities in `utils/ai_analysis.py`
- Asynchronous processing with progress callbacks

### Data Architecture

**Database**: PostgreSQL (primary) with SQLite fallback for development
- SSL-enabled connections for production deployment
- Connection pooling with SQLAlchemy engine configuration
- Automatic migration system using Flask-Migrate/Alembic

**Core Data Models** (FHIR-influenced):
- `Patient`: Demographics, identifiers, addresses (FHIR Patient resource)
- `Condition`: Clinical conditions with ICD-10 coding (FHIR Condition resource)
- `Document`: Clinical notes with MEAT/TAMPER fields
- `AssessmentTool`: Configurable clinical assessment instruments
- `AssessmentResult`: Completed assessments with scoring
- `AuditLog`: Comprehensive activity tracking with before/after values

**Key Schema Decisions**:
- Separate `PatientIdentifier` table for multiple identifier types (MRN, SSN, etc.)
- JSON fields for flexible assessment tool configuration (`scoring_logic`, `options`)
- Bi-directional relationships between documents and patients
- Unique constraints with partial indexes (PostgreSQL-specific for nullable fields)

### Authentication & Authorization

**Strategy**: Role-based access control (RBAC)
- Two primary roles: 'user' and 'admin'
- Flask-Login for session management
- Werkzeug password hashing (PBKDF2)
- Decorator-based route protection (`@admin_required`)

**Audit Trail**:
- Comprehensive logging of all CRUD operations
- Before/after value tracking for data changes
- IP address and user agent capture
- Indexed queries for audit log search performance

### External Dependencies

**AI Services**:
- OpenAI API: GPT-4 for clinical text analysis and MEAT criteria extraction
- OpenAI Whisper: Audio-to-text transcription (may be local or API-based)
- Speech Recognition library: Fallback transcription option

**Third-Party Libraries**:
- Flask ecosystem: Flask-Login, Flask-Migrate, Flask-SQLAlchemy
- SQLAlchemy: Database ORM with PostgreSQL dialect
- Psycopg2: PostgreSQL database adapter
- python-docx: DOCX file processing
- pydub: Audio format conversion

**Database Services**:
- PostgreSQL (primary): Production database with SSL
- SQLite: Development/testing fallback
- SSL/TLS: Certificate-based encryption for database connections

**Frontend Dependencies**:
- Bootstrap 5.3: UI framework
- Bootstrap Icons: Icon set
- WebRTC: Browser-based audio/video capture (native browser API)

**Clinical Standards**:
- FHIR R6 (structure definitions referenced): Patient, Condition resources
- ICD-10 code system: Diagnosis and condition coding
- COWS assessment: Clinical Opiate Withdrawal Scale
- PRAPARE assessment: Social determinants of health screening

**Deployment Considerations**:
- Replit environment variables for configuration
- File upload handling with secure filename sanitization
- SSL certificate bundle at `/etc/ssl/certs/ca-certificates.crt`
- Environment-based configuration (DATABASE_URL detection)