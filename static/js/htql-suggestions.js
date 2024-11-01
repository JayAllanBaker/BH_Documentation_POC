class HTQLSuggestions {
    constructor(inputElement) {
        if (!inputElement) {
            console.error('Input element not provided');
            return;
        }
        console.log('Initializing HTQLSuggestions with input:', inputElement);
        
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
                'code': 'Search by condition code',
                'status': 'Filter by condition status',
                'severity': 'Filter by severity'
            }
        };
        this.operators = ['AND', 'OR', 'NOT'];
        
        // Force suggestions list creation in constructor
        this.createSuggestionsList();
        this.setupEventListeners();
        
        // Test initialization
        console.log('Suggestions list created:', this.suggestionsList);
        console.log('Input element ready:', this.input);
    }

    createSuggestionsList() {
        console.log('Creating suggestions list');
        
        // Remove existing suggestions list if present
        const existingList = document.getElementById('htqlSuggestionsList');
        if (existingList) {
            existingList.remove();
        }
        
        this.suggestionsList = document.createElement('ul');
        this.suggestionsList.className = 'suggestions-list';
        this.suggestionsList.id = 'htqlSuggestionsList';
        this.suggestionsList.style.cssText = `
            display: block !important;
            position: absolute !important;
            z-index: 99999 !important;
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
        
        // Insert suggestions list after input
        this.input.parentNode.appendChild(this.suggestionsList);
        console.log('Suggestions list created:', this.suggestionsList);
    }

    setupEventListeners() {
        this.input.addEventListener('input', () => {
            console.log('Input event triggered');
            this.showLoadingIndicator();
            
            // Clear any existing timeout
            if (this.inputTimeout) {
                clearTimeout(this.inputTimeout);
            }
            
            // Debounce input handling
            this.inputTimeout = setTimeout(() => this.handleInput(), 150);
        });

        this.input.addEventListener('keydown', (e) => {
            console.log('Keydown event:', e.key);
            this.handleKeydown(e);
        });

        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.suggestionsList.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    handleInput() {
        console.log('Input event triggered');
        const inputValue = this.input.value;
        console.log('Current input value:', inputValue);
        
        // Clear any existing timeout
        if (this.inputTimeout) {
            clearTimeout(this.inputTimeout);
        }
        
        // Debounce input handling
        this.inputTimeout = setTimeout(() => {
            try {
                if (inputValue.includes('.') || inputValue.includes(':')) {
                    this.generateSuggestions(inputValue);
                    if (this.currentSuggestions.length > 0) {
                        this.showSuggestions();
                        console.log('Suggestions shown:', this.currentSuggestions.length);
                    }
                } else {
                    this.hideSuggestions();
                }
            } catch (error) {
                console.error('Error handling input:', error);
            }
        }, 150);
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
        console.log('Showing suggestions:', this.currentSuggestions);
        if (!this.suggestionsList) {
            console.error('Suggestions list not initialized, recreating...');
            this.createSuggestionsList();
        }

        try {
            this.selectedIndex = -1;
            
            // Force visibility
            this.suggestionsList.style.display = 'block';
            this.suggestionsList.style.visibility = 'visible';
            this.suggestionsList.style.opacity = '1';
            
            // Update content
            this.suggestionsList.innerHTML = this.currentSuggestions
                .map((suggestion, index) => `
                    <li class="suggestion-item" data-index="${index}">
                        ${suggestion}
                        ${this.getDescription(suggestion)}
                    </li>
                `)
                .join('');
                
            console.log('Suggestions list state:', {
                display: this.suggestionsList.style.display,
                visibility: this.suggestionsList.style.visibility,
                opacity: this.suggestionsList.style.opacity,
                height: this.suggestionsList.offsetHeight,
                children: this.suggestionsList.children.length
            });

            // Add click handlers
            this.suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    const index = parseInt(item.dataset.index);
                    this.applySuggestion(this.currentSuggestions[index]);
                });
            });
        } catch (error) {
            console.error('Error showing suggestions:', error);
        }
    }

    hideSuggestions() {
        if (this.suggestionsList) {
            this.suggestionsList.style.display = 'none';
            this.currentSuggestions = [];
            this.selectedIndex = -1;
        }
    }

    getDescription(suggestion) {
        if (suggestion.includes('.')) {
            const [category, field] = suggestion.split('.');
            return this.fields[category][field] ? 
                `<small> - ${this.fields[category][field]}</small>` : '';
        }
        return '';
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
                    this.applySuggestion(this.currentSuggestions[this.selectedIndex]);
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
