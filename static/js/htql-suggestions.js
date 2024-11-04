class HTQLSuggestions {
    constructor(input) {
        this.input = input;
        this.suggestionsList = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.loadingIndicator = null;
        this.lastQuery = '';
        this.lastRequestTime = 0;
        this.debounceDelay = 300;
        
        this.setupEventListeners();
        this.createLoadingIndicator();
        console.log('HTQLSuggestions initialized');
    }

    setupEventListeners() {
        this.input.addEventListener('input', () => this.handleInput());
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    createLoadingIndicator() {
        this.loadingIndicator = document.getElementById('htqlLoadingIndicator');
    }

    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.remove('d-none');
        }
    }

    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.add('d-none');
        }
    }

    validateSyntax(query) {
        if (!query) return true;
        
        const validationIndicator = this.input.parentNode.querySelector('.validation-indicator');
        if (!validationIndicator) return true;

        // Remove existing classes
        validationIndicator.classList.remove('bg-success', 'bg-danger');
        
        // Basic syntax validation rules
        const validPatterns = [
            /^[a-z]+$/,  // Single word (category)
            /^[a-z]+\.$/,  // Category with dot
            /^[a-z]+\.[a-z]+$/,  // Category.field
            /^[a-z]+\.[a-z]+:.*$/,  // Category.field:value
            /^.*\s+(AND|OR|NOT)\s+.*$/  // Logical operators
        ];
        
        // Invalid patterns
        const invalidPatterns = [
            /^[a-z]+:.+$/,  // Missing field (e.g., patient:value)
            /^[^a-z\s]+/,  // Starting with non-letter
            /\s+$/,  // Ending with whitespace
            /:[^a-z0-9\s]/,  // Invalid characters after colon
            /\.[^a-z]/  // Invalid characters after dot
        ];
        
        // Check for invalid patterns first
        const hasInvalidPattern = invalidPatterns.some(pattern => pattern.test(query.toLowerCase()));
        if (hasInvalidPattern) {
            validationIndicator.classList.add('bg-danger');
            console.log('Invalid syntax:', query);
            return false;
        }
        
        // Check for valid patterns
        const isValid = validPatterns.some(pattern => pattern.test(query.toLowerCase()));
        validationIndicator.classList.add(isValid ? 'bg-success' : 'bg-danger');
        console.log('Query:', query, 'Valid:', isValid);
        
        return isValid;
    }

    async handleInput() {
        const inputValue = this.input.value;
        const currentTime = Date.now();
        
        // Always validate syntax first
        this.validateSyntax(inputValue);
        
        // Debounce API calls
        if (currentTime - this.lastRequestTime < this.debounceDelay) {
            return;
        }
        
        try {
            // Handle ICD-10 and SNOMED CT code suggestions
            if (inputValue.includes('condition.code:')) {
                const parts = inputValue.split('condition.code:');
                const searchTerm = parts[1].trim();
                
                if (searchTerm && searchTerm !== this.lastQuery) {
                    this.lastQuery = searchTerm;
                    this.lastRequestTime = currentTime;
                    this.showLoading();
                    
                    // Fetch both ICD-10 and SNOMED CT suggestions
                    const response = await fetch(`/api/code-suggestions?q=${encodeURIComponent(searchTerm)}`);
                    if (response.ok) {
                        const suggestions = await response.json();
                        this.currentSuggestions = suggestions.map(s => ({
                            text: `condition.code:${s.code}`,
                            displayText: `${s.code} - ${s.description}`,
                            details: `(${s.system})`
                        }));
                        if (this.currentSuggestions.length > 0) {
                            this.showSuggestions();
                        }
                    }
                }
            } else if (inputValue.includes('.') || inputValue.includes(':')) {
                this.generateFieldSuggestions(inputValue);
                if (this.currentSuggestions.length > 0) {
                    this.showSuggestions();
                } else {
                    this.hideSuggestions();
                }
            } else {
                this.generateFieldSuggestions(inputValue);
                if (this.currentSuggestions.length > 0) {
                    this.showSuggestions();
                } else {
                    this.hideSuggestions();
                }
            }
        } catch (error) {
            console.error('Error handling input:', error);
        } finally {
            this.hideLoading();
        }
    }

    handleKeydown(e) {
        if (!this.suggestionsList) return;
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectNext();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectPrevious();
                break;
            case 'Enter':
            case 'Tab':
                e.preventDefault();
                this.applyCurrent();
                break;
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }

    selectNext() {
        if (this.selectedIndex < this.currentSuggestions.length - 1) {
            this.selectedIndex++;
            this.updateSelection();
        }
    }

    selectPrevious() {
        if (this.selectedIndex > 0) {
            this.selectedIndex--;
            this.updateSelection();
        }
    }

    updateSelection() {
        const items = this.suggestionsList.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedIndex);
        });
    }

    applyCurrent() {
        if (this.selectedIndex >= 0 && this.selectedIndex < this.currentSuggestions.length) {
            this.applySuggestion(this.currentSuggestions[this.selectedIndex].text);
        }
    }

    applySuggestion(suggestion) {
        const cursorPosition = this.input.selectionStart;
        const inputValue = this.input.value;
        const beforeCursor = inputValue.substring(0, cursorPosition);
        const afterCursor = inputValue.substring(cursorPosition);
        
        const lastSpaceIndex = beforeCursor.lastIndexOf(' ');
        const start = lastSpaceIndex === -1 ? 0 : lastSpaceIndex + 1;
        
        this.input.value = beforeCursor.substring(0, start) + suggestion + afterCursor;
        const newPosition = start + suggestion.length;
        this.input.setSelectionRange(newPosition, newPosition);
        this.input.focus();
        
        this.hideSuggestions();
    }

    showSuggestions() {
        if (!this.suggestionsList) {
            this.suggestionsList = document.createElement('ul');
            this.suggestionsList.className = 'suggestions-list';
            this.input.parentNode.appendChild(this.suggestionsList);
        }

        this.suggestionsList.innerHTML = this.currentSuggestions.map((suggestion, index) => `
            <li class="suggestion-item ${index === this.selectedIndex ? 'selected' : ''}"
                data-index="${index}">
                <strong>${suggestion.displayText}</strong>
                ${suggestion.details ? `<small class="text-muted"> ${suggestion.details}</small>` : ''}
            </li>
        `).join('');

        this.suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.selectedIndex = index;
                this.applyCurrent();
            });
        });

        this.suggestionsList.classList.remove('d-none');
    }

    hideSuggestions() {
        if (this.suggestionsList) {
            this.suggestionsList.classList.add('d-none');
        }
        this.selectedIndex = -1;
    }

    generateFieldSuggestions(query) {
        const suggestions = [];
        const categories = ['patient', 'document', 'condition'];
        
        // Add category suggestions
        if (!query.includes('.')) {
            suggestions.push(...categories
                .filter(c => c.toLowerCase().startsWith(query.toLowerCase()))
                .map(c => ({
                    text: `${c}.`,
                    displayText: `${c}`,
                    details: 'Select a field'
                })));
        }
        
        // Field suggestions
        if (query.includes('.')) {
            const [category, field] = query.split('.');
            const fields = {
                'patient': ['name', 'id', 'gender', 'city', 'state'],
                'document': ['title', 'content', 'transcription'],
                'condition': ['code', 'status', 'severity']
            };
            
            if (category in fields) {
                suggestions.push(...fields[category]
                    .filter(f => !field || f.toLowerCase().startsWith(field.toLowerCase()))
                    .map(f => ({
                        text: `${category}.${f}:`,
                        displayText: `${category}.${f}`,
                        details: `field type: ${f}`
                    })));
            }
        }
        
        this.currentSuggestions = suggestions;
    }
}
