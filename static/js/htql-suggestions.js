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
        
        // Force suggestions list creation in constructor
        this.createSuggestionsList();
        this.setupEventListeners();
        
        // Test initialization
        console.log('Suggestions list created:', this.suggestionsList);
        console.log('Input element ready:', this.input);

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
    }

    createSuggestionsList() {
        console.log('Creating suggestions list');
        
        // Remove existing suggestions list if present
        if (this.suggestionsList) {
            this.suggestionsList.remove();
        }
        
        this.suggestionsList = document.createElement('ul');
        this.suggestionsList.className = 'suggestions-list';
        this.suggestionsList.id = 'htqlSuggestionsList';
        
        // Position wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'position-relative w-100';
        wrapper.style.zIndex = '1050';
        
        // Move input into wrapper and append suggestions list
        this.input.parentNode.insertBefore(wrapper, this.input);
        wrapper.appendChild(this.input);
        wrapper.appendChild(this.suggestionsList);
        
        console.log('Suggestions list created:', this.suggestionsList);
    }

    setupEventListeners() {
        console.log('Setting up event listeners');
        
        this.input.addEventListener('input', () => {
            console.log('Input event triggered');
            this.showLoadingIndicator();
            if (this.debounceTimeout) clearTimeout(this.debounceTimeout);
            this.debounceTimeout = setTimeout(() => this.handleInput(), 150);
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
        
        if (!this.suggestionsList) {
            console.error('Suggestions list not initialized');
            return;
        }

        try {
            const cursorPosition = this.input.selectionStart;
            const tokens = this.tokenize(inputValue.substring(0, cursorPosition));
            const currentToken = tokens[tokens.length - 1] || '';

            if (inputValue.includes('.') || inputValue.includes(':')) {
                this.generateSuggestions(currentToken);
                // Force suggestions visibility
                if (this.currentSuggestions.length > 0) {
                    this.suggestionsList.style.display = 'block';
                    this.suggestionsList.style.visibility = 'visible';
                    console.log('Suggestions forced visible');
                }
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

        if (this.currentSuggestions.length > 0) {
            this.showSuggestions();
        } else {
            this.hideSuggestions();
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
            this.suggestionsList.style.display = 'block';
            this.suggestionsList.innerHTML = this.currentSuggestions
                .map((suggestion, index) => `
                    <li class="suggestion-item" data-index="${index}">
                        ${suggestion}
                        ${this.getDescription(suggestion)}
                    </li>
                `)
                .join('');
                
            console.log('Suggestions list visibility:', 
                this.suggestionsList.style.display,
                'Height:', this.suggestionsList.offsetHeight,
                'Children:', this.suggestionsList.children.length);

            // Add click handlers to suggestions
            this.suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    const index = parseInt(item.dataset.index);
                    this.applySuggestion(this.currentSuggestions[index]);
                });
                item.addEventListener('mouseenter', () => {
                    this.selectedIndex = parseInt(item.dataset.index);
                    this.updateSelection();
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
        if (!this.suggestionsList) return;

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
