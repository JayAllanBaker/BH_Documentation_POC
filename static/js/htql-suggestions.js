class HTQLSuggestions {
    constructor(inputElement) {
        console.log('Initializing HTQLSuggestions');
        this.input = inputElement;
        this.suggestionsList = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.loadingIndicator = document.getElementById('htqlLoadingIndicator');
        this.debounceTimeout = null;
        
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
        
        this.setupEventListeners();
        console.log('HTQLSuggestions initialized successfully');
    }

    setupEventListeners() {
        console.log('Setting up event listeners');
        try {
            // Create suggestions container
            this.suggestionsList = document.createElement('ul');
            this.suggestionsList.className = 'suggestions-list d-none';
            
            // Create wrapper for proper positioning
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            wrapper.style.flex = '1';
            
            // Insert wrapper and move input into it
            this.input.parentNode.insertBefore(wrapper, this.input);
            wrapper.appendChild(this.input);
            wrapper.appendChild(this.suggestionsList);

            // Input event with debouncing
            this.input.addEventListener('input', () => {
                console.log('Input event fired');
                this.showLoadingIndicator();
                clearTimeout(this.debounceTimeout);
                this.debounceTimeout = setTimeout(() => {
                    this.handleInput();
                }, 150);
            });
            
            // Keyboard navigation
            this.input.addEventListener('keydown', (e) => {
                console.log('Keydown event fired:', e.key);
                this.handleKeydown(e);
            });
            
            // Click outside to close
            document.addEventListener('click', (e) => {
                if (!this.input.contains(e.target) && !this.suggestionsList.contains(e.target)) {
                    console.log('Clicking outside, hiding suggestions');
                    this.hideSuggestions();
                }
            });

            console.log('Event listeners setup completed');
        } catch (error) {
            console.error('Error setting up event listeners:', error);
        }
    }

    showLoadingIndicator() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'block';
        }
    }

    hideLoadingIndicator() {
        if (this.loadingIndicator) {
            this.loadingIndicator.style.display = 'none';
        }
    }

    handleInput() {
        try {
            const cursorPosition = this.input.selectionStart;
            const inputValue = this.input.value;
            const tokens = this.tokenize(inputValue.substring(0, cursorPosition));
            const currentToken = tokens[tokens.length - 1] || '';
            
            console.log('Processing input:', { currentToken, tokens });

            if (currentToken.includes('.')) {
                // Suggesting field values
                const [category, field] = currentToken.split('.');
                if (this.fields[category]) {
                    this.currentSuggestions = Object.keys(this.fields[category])
                        .filter(f => !field || f.toLowerCase().startsWith(field.toLowerCase()))
                        .map(f => `${category}.${f}`);
                }
            } else if (currentToken.includes(':')) {
                // Suggesting values based on field type
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
                // Suggesting categories or operators
                const suggestions = [...Object.keys(this.fields), ...this.operators];
                this.currentSuggestions = suggestions.filter(s => 
                    !currentToken || s.toLowerCase().startsWith(currentToken.toLowerCase())
                );
            }

            console.log('Generated suggestions:', this.currentSuggestions);
            
            if (this.currentSuggestions.length > 0) {
                this.showSuggestions();
            } else {
                this.hideSuggestions();
            }
        } catch (error) {
            console.error('Error handling input:', error);
        } finally {
            this.hideLoadingIndicator();
        }
    }

    handleKeydown(e) {
        if (this.currentSuggestions.length === 0) return;

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

    tokenize(text) {
        return text.split(/\s+/).filter(Boolean);
    }

    showSuggestions() {
        try {
            console.log('Showing suggestions');
            this.selectedIndex = -1;
            this.suggestionsList.innerHTML = this.currentSuggestions
                .map((suggestion, index) => `
                    <li class="suggestion-item" data-index="${index}">
                        ${suggestion}
                        ${this.getDescription(suggestion)}
                    </li>
                `)
                .join('');

            this.suggestionsList.classList.remove('d-none');
            this.suggestionsList.classList.add('show');
            
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

    getDescription(suggestion) {
        if (suggestion.includes('.')) {
            const [category, field] = suggestion.split('.');
            return this.fields[category][field] ? 
                `<small> - ${this.fields[category][field]}</small>` : '';
        }
        return '';
    }

    hideSuggestions() {
        console.log('Hiding suggestions');
        this.suggestionsList.classList.remove('show');
        this.suggestionsList.classList.add('d-none');
        this.currentSuggestions = [];
        this.selectedIndex = -1;
    }

    updateSelection() {
        const items = this.suggestionsList.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
                // Ensure selected item is visible in viewport
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    applySuggestion(suggestion) {
        try {
            console.log('Applying suggestion:', suggestion);
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
        } catch (error) {
            console.error('Error applying suggestion:', error);
        }
    }
}
