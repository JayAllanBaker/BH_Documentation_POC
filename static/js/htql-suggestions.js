class HTQLSuggestions {
    constructor(inputElement) {
        console.log('Initializing HTQLSuggestions');
        this.input = inputElement;
        this.suggestionsList = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
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
        console.log('HTQLSuggestions initialized');
    }

    setupEventListeners() {
        console.log('Setting up event listeners');
        
        // Create suggestions container
        this.suggestionsList = document.createElement('ul');
        this.suggestionsList.className = 'suggestions-list d-none';
        
        // Find the input's container (the input-group div)
        const inputGroup = this.input.closest('.input-group');
        if (!inputGroup) {
            console.error('Could not find input-group container');
            return;
        }
        
        // Create a wrapper div for proper positioning
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.flex = '1';
        
        // Move input to wrapper
        this.input.parentNode.insertBefore(wrapper, this.input);
        wrapper.appendChild(this.input);
        wrapper.appendChild(this.suggestionsList);

        this.input.addEventListener('input', () => {
            console.log('Input event fired');
            this.handleInput();
        });
        
        this.input.addEventListener('keydown', (e) => {
            console.log('Keydown event fired:', e.key);
            this.handleKeydown(e);
        });
        
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.suggestionsList.contains(e.target)) {
                console.log('Clicking outside, hiding suggestions');
                this.hideSuggestions();
            }
        });
    }

    handleInput() {
        const cursorPosition = this.input.selectionStart;
        const inputValue = this.input.value;
        const tokens = this.tokenize(inputValue.substring(0, cursorPosition));
        const currentToken = tokens[tokens.length - 1] || '';
        
        console.log('Current token:', currentToken);

        if (currentToken.includes('.')) {
            // Suggesting field values
            const [category, field] = currentToken.split('.');
            if (this.fields[category]) {
                this.currentSuggestions = Object.keys(this.fields[category])
                    .filter(f => !field || f.startsWith(field))
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

        console.log('Current suggestions:', this.currentSuggestions);
        
        if (this.currentSuggestions.length > 0) {
            this.showSuggestions();
        } else {
            this.hideSuggestions();
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
    }

    getDescription(suggestion) {
        if (suggestion.includes('.')) {
            const [category, field] = suggestion.split('.');
            return this.fields[category][field] ? 
                `<small class="text-muted"> - ${this.fields[category][field]}</small>` : '';
        }
        return '';
    }

    hideSuggestions() {
        console.log('Hiding suggestions');
        this.suggestionsList.classList.add('d-none');
        this.currentSuggestions = [];
        this.selectedIndex = -1;
    }

    updateSelection() {
        const items = this.suggestionsList.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    applySuggestion(suggestion) {
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
    }
}
