class HTQLSuggestions {
    constructor(inputElement) {
        console.log('Initializing HTQLSuggestions');
        if (!inputElement) {
            throw new Error('Input element is required');
        }

        this.input = inputElement;
        this.suggestionsList = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.loadingIndicator = document.getElementById('htqlLoadingIndicator');
        this.debounceTimeout = null;
        this.retryCount = 0;
        this.maxRetries = 3;

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

        this.initializeSuggestions();
    }

    initializeSuggestions() {
        console.log('Attempting to initialize suggestions (attempt ' + (this.retryCount + 1) + ')');
        try {
            // Create suggestions container
            this.suggestionsList = document.createElement('ul');
            this.suggestionsList.id = 'htqlSuggestionsList';
            this.suggestionsList.className = 'suggestions-list d-none';
            console.log('Created suggestions list:', this.suggestionsList);

            if (!this.suggestionsList) {
                console.error('Failed to create suggestions list');
                this.retryInitialization();
                return;
            }

            // Set up input container
            const wrapper = document.createElement('div');
            wrapper.className = 'htql-input-wrapper';
            
            // Insert wrapper and move input into it
            this.input.parentNode.insertBefore(wrapper, this.input);
            wrapper.appendChild(this.input);
            wrapper.appendChild(this.suggestionsList);
            console.log('Set up input wrapper and positioned elements');

            this.setupEventListeners();
            console.log('HTQLSuggestions initialized successfully');
        } catch (error) {
            console.error('Error initializing suggestions:', error);
            this.retryInitialization();
        }
    }

    retryInitialization() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log('Retrying initialization in 100ms...');
            setTimeout(() => this.initializeSuggestions(), 100);
        } else {
            console.error('Failed to initialize suggestions after ' + this.maxRetries + ' attempts');
        }
    }

    setupEventListeners() {
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

    handleInput() {
        console.log('Handling input event');
        try {
            const cursorPosition = this.input.selectionStart;
            const inputValue = this.input.value;
            const tokens = this.tokenize(inputValue.substring(0, cursorPosition));
            const currentToken = tokens[tokens.length - 1] || '';

            console.log('Processing input:', { currentToken, tokens });

            if (currentToken.includes('.')) {
                // Suggesting field values
                const [category, field] = currentToken.split('.');
                console.log('Processing category.field suggestion:', { category, field });
                if (this.fields[category]) {
                    this.currentSuggestions = Object.keys(this.fields[category])
                        .filter(f => !field || f.toLowerCase().startsWith(field.toLowerCase()))
                        .map(f => `${category}.${f}`);
                }
            } else if (currentToken.includes(':')) {
                // Suggesting values based on field type
                const [field, value] = currentToken.split(':');
                console.log('Processing field:value suggestion:', { field, value });
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
                console.log('Processing category/operator suggestions');
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
        if (!this.suggestionsList) {
            console.error('Suggestions list element not found');
            return;
        }

        console.log('Showing suggestions');
        this.selectedIndex = -1;
        
        try {
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
            console.log('Suggestions list shown');

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
        if (!this.suggestionsList) return;
        
        console.log('Hiding suggestions');
        this.suggestionsList.classList.remove('show');
        this.suggestionsList.classList.add('d-none');
        this.currentSuggestions = [];
        this.selectedIndex = -1;
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
        console.log('Applying suggestion:', suggestion);
        try {
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
