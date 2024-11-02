class HTQLSuggestions {
    constructor(input) {
        this.input = input;
        this.suggestionsList = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.loadingIndicator = null;
        
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
        
        // Basic syntax validation rules
        const validPatterns = [
            /^[a-z]+$/,  // Single word (category)
            /^[a-z]+\.$/,  // Category with dot
            /^[a-z]+\.[a-z]+$/,  // Category.field
            /^[a-z]+\.[a-z]+:.*$/,  // Category.field:value
            /^.*\s+(AND|OR|NOT)\s+.*$/  // Logical operators
        ];
        
        // Invalid patterns that should show red indicator
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
            const validationIndicator = this.input.parentNode.querySelector('.validation-indicator');
            if (validationIndicator) {
                validationIndicator.classList.remove('bg-success', 'bg-danger');
                validationIndicator.classList.add('bg-danger');
                console.log('Query failed invalid pattern check:', query);
            }
            return false;
        }
        
        // Test if query matches any valid pattern
        const isValid = validPatterns.some(pattern => pattern.test(query.toLowerCase()));
        
        // Update validation indicator
        const validationIndicator = this.input.parentNode.querySelector('.validation-indicator');
        if (validationIndicator) {
            validationIndicator.classList.remove('bg-success', 'bg-danger');
            validationIndicator.classList.add(isValid ? 'bg-success' : 'bg-danger');
            console.log('Query:', query);
            console.log('Is valid:', isValid);
        }
        
        return isValid;
    }

    async handleInput() {
        const inputValue = this.input.value;
        
        // Always validate syntax first
        this.validateSyntax(inputValue);
        
        try {
            if (inputValue.includes('condition.code:')) {
                const parts = inputValue.split('condition.code:');
                const searchTerm = parts[1].trim();
                
                if (searchTerm) {
                    this.showLoading();
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
                    this.hideLoading();
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
            this.hideLoading();
        }
    }

    // Rest of the class implementation remains the same...
    [Previous implementation of other methods]
}
