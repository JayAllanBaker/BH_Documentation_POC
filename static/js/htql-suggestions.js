class HTQLSuggestions {
    constructor(inputElement) {
        if (!inputElement) {
            console.error('Input element not provided');
            return;
        }
        
        this.input = inputElement;
        this.suggestionsList = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.loadingIndicator = document.getElementById('htqlLoadingIndicator');
        
        // Initialize field mappings
        this.fields = {
            'patient': {
                'name': 'Search patient names',
                'id': 'Search by patient ID',
                'gender': 'Filter by gender',
                'city': 'Search by city',
                'state': 'Filter by state'
            },
            'document': {
                'title': 'Search document titles',
                'content': 'Search document content',
                'transcription': 'Search transcriptions'
            },
            'condition': {
                'code': 'Search by condition code (ICD-10 or SNOMED CT)',
                'status': 'Filter by condition status',
                'severity': 'Filter by severity'
            }
        };
        
        this.operators = ['AND', 'OR', 'NOT'];
        
        // Create suggestions list in constructor
        this.createSuggestionsList();
        this.setupEventListeners();
    }

    createSuggestionsList() {
        // Remove existing suggestions list if present
        const existingList = document.getElementById('htqlSuggestionsList');
        if (existingList) {
            existingList.remove();
        }
        
        this.suggestionsList = document.createElement('ul');
        this.suggestionsList.className = 'suggestions-list';
        this.suggestionsList.id = 'htqlSuggestionsList';
        this.suggestionsList.style.cssText = `
            display: none;
            position: absolute;
            z-index: 99999;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ced4da;
            border-radius: 0.375rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-height: 300px;
            overflow-y: auto;
            margin-top: 2px;
            padding: 0;
        `;
        
        this.input.parentNode.appendChild(this.suggestionsList);
    }

    setupEventListeners() {
        this.input.addEventListener('input', () => {
            this.showLoadingIndicator();
            
            if (this.inputTimeout) {
                clearTimeout(this.inputTimeout);
            }
            
            this.inputTimeout = setTimeout(() => this.handleInput(), 150);
        });

        this.input.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });

        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.suggestionsList.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    async handleInput() {
        const inputValue = this.input.value;
        console.log('Input value:', inputValue);
        
        try {
            if (inputValue.includes('condition.code:')) {
                const parts = inputValue.split('condition.code:');
                const searchTerm = parts[1].trim();
                
                if (searchTerm) {
                    const response = await fetch(`/api/code-suggestions?q=${encodeURIComponent(searchTerm)}`);
                    if (response.ok) {
                        const suggestions = await response.json();
                        this.currentSuggestions = suggestions.map(s => 
                            `condition.code:${s.code} /* ${s.description} (${s.system}) */`
                        );
                        if (this.currentSuggestions.length > 0) {
                            this.showSuggestions();
                        }
                    }
                }
            } else if (inputValue.includes('.') || inputValue.includes(':')) {
                this.generateSuggestions(inputValue);
                if (this.currentSuggestions.length > 0) {
                    this.showSuggestions();
                }
            } else {
                this.hideSuggestions();
            }
        } catch (error) {
            console.error('Error handling input:', error);
        } finally {
            this.hideLoadingIndicator();
        }
    }

    generateSuggestions(currentToken) {
        if (currentToken.includes('.')) {
            const [category, field] = currentToken.split('.');
            if (this.fields[category]) {
                this.currentSuggestions = Object.keys(this.fields[category])
                    .filter(f => !field || f.toLowerCase().startsWith(field.toLowerCase()))
                    .map(f => `${category}.${f}`);
            }
        } else if (currentToken.includes(':')) {
            const [field, value] = currentToken.split(':');
            if (field.includes('gender')) {
                this.currentSuggestions = ['male', 'female', 'other']
                    .filter(v => !value || v.startsWith(value.toLowerCase()))
                    .map(v => `${field}:${v}`);
            } else if (field.includes('status')) {
                this.currentSuggestions = ['active', 'inactive', 'resolved']
                    .filter(v => !value || v.startsWith(value.toLowerCase()))
                    .map(v => `${field}:${v}`);
            } else if (field.includes('severity')) {
                this.currentSuggestions = ['mild', 'moderate', 'severe']
                    .filter(v => !value || v.startsWith(value.toLowerCase()))
                    .map(v => `${field}:${v}`);
            }
        } else {
            const suggestions = [...Object.keys(this.fields), ...this.operators];
            this.currentSuggestions = suggestions.filter(s => 
                !currentToken || s.toLowerCase().startsWith(currentToken.toLowerCase())
            );
        }
    }

    showSuggestions() {
        if (!this.suggestionsList) {
            this.createSuggestionsList();
        }

        this.selectedIndex = -1;
        this.suggestionsList.style.display = 'block';
        
        this.suggestionsList.innerHTML = this.currentSuggestions
            .map((suggestion, index) => {
                let displayText = suggestion;
                let additionalClass = '';
                
                // Handle code suggestions with comments
                if (suggestion.includes('/*')) {
                    const [code, comment] = suggestion.split('/*');
                    displayText = `
                        <div class="suggestion-code">${code.trim()}</div>
                        <small class="suggestion-comment text-muted">${comment.replace('*/', '').trim()}</small>
                    `;
                    additionalClass = 'code-suggestion';
                }
                
                return `
                    <li class="suggestion-item ${additionalClass}" data-index="${index}">
                        ${displayText}
                    </li>
                `;
            })
            .join('');

        // Add click handlers
        this.suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                let suggestion = this.currentSuggestions[index];
                
                // Remove comments from code suggestions
                if (suggestion.includes('/*')) {
                    suggestion = suggestion.split('/*')[0].trim();
                }
                
                this.applySuggestion(suggestion);
            });
        });
    }

    hideSuggestions() {
        if (this.suggestionsList) {
            this.suggestionsList.style.display = 'none';
            this.currentSuggestions = [];
            this.selectedIndex = -1;
        }
    }

    handleKeydown(e) {
        if (!this.suggestionsList || this.currentSuggestions.length === 0) return;

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, this.currentSuggestions.length - 1);
                this.updateSelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
                this.updateSelection();
                break;
            case 'Tab':
            case 'Enter':
                if (this.selectedIndex >= 0) {
                    e.preventDefault();
                    let suggestion = this.currentSuggestions[this.selectedIndex];
                    if (suggestion.includes('/*')) {
                        suggestion = suggestion.split('/*')[0].trim();
                    }
                    this.applySuggestion(suggestion);
                }
                break;
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }

    updateSelection() {
        const items = this.suggestionsList.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    applySuggestion(suggestion) {
        const cursorPosition = this.input.selectionStart;
        const inputValue = this.input.value;
        const tokens = this.tokenize(inputValue.substring(0, cursorPosition));
        const beforeLastToken = tokens.slice(0, -1).join(' ');
        const afterCursor = inputValue.substring(cursorPosition);

        this.input.value = beforeLastToken + 
            (beforeLastToken ? ' ' : '') + 
            suggestion + 
            (afterCursor.startsWith(' ') ? '' : ' ') + 
            afterCursor;

        const newPosition = (beforeLastToken ? beforeLastToken + ' ' : '').length + suggestion.length + 1;
        this.input.setSelectionRange(newPosition, newPosition);
        this.hideSuggestions();
        this.input.focus();
    }

    tokenize(text) {
        return text.split(/\s+/).filter(Boolean);
    }

    showLoadingIndicator() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.remove('d-none');
        }
    }

    hideLoadingIndicator() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.add('d-none');
        }
    }
}
