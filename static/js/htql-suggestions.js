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

    async handleInput() {
        const inputValue = this.input.value;
        console.log('Input value:', inputValue);
        
        try {
            if (inputValue.includes('condition.code:')) {
                const parts = inputValue.split('condition.code:');
                const searchTerm = parts[1].trim();
                
                if (searchTerm) {
                    this.showLoading();
                    const response = await fetch(`/api/code-suggestions?q=${encodeURIComponent(searchTerm)}`);
                    if (response.ok) {
                        const suggestions = await response.json();
                        console.log('Received suggestions:', suggestions);
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
                } else {
                    this.hideSuggestions();
                }
            } else if (inputValue.includes('.') || inputValue.includes(':')) {
                this.generateFieldSuggestions(inputValue);
                if (this.currentSuggestions.length > 0) {
                    this.showSuggestions();
                } else {
                    this.hideSuggestions();
                }
            } else {
                this.hideSuggestions();
            }
        } catch (error) {
            console.error('Error handling input:', error);
            this.hideLoading();
        }
    }

    generateFieldSuggestions(query) {
        const suggestions = [];
        
        if (query.includes('.')) {
            const [category, field] = query.split('.');
            const fields = {
                'patient': ['name', 'id', 'gender', 'city', 'state'],
                'document': ['title', 'content', 'transcription'],
                'condition': ['code', 'status', 'severity']
            };
            
            const fieldValues = {
                'condition.status': ['active', 'inactive', 'resolved', 'recurrence', 'relapse', 'remission'],
                'condition.severity': ['mild', 'moderate', 'severe'],
                'patient.gender': ['male', 'female', 'other']
            };
            
            const fullField = query.trim();
            if (fieldValues[fullField]) {
                suggestions.push(...fieldValues[fullField].map(v => ({
                    text: `${fullField}:${v}`,
                    displayText: `${fullField}:${v}`,
                    details: null
                })));
            }
            else if (!field || field === '') {
                if (fields[category]) {
                    suggestions.push(...fields[category].map(f => ({
                        text: `${category}.${f}`,
                        displayText: `${category}.${f}`,
                        details: null
                    })));
                }
            }
            else if (fields[category]) {
                suggestions.push(...fields[category]
                    .filter(f => f.startsWith(field))
                    .map(f => ({
                        text: `${category}.${f}`,
                        displayText: `${category}.${f}`,
                        details: null
                    })));
            }
        }
        
        this.currentSuggestions = suggestions;
    }

    showSuggestions() {
        if (!this.suggestionsList) {
            this.createSuggestionsList();
        }

        this.selectedIndex = -1;
        this.suggestionsList.style.display = 'block';
        
        this.suggestionsList.innerHTML = this.currentSuggestions
            .map((suggestion, index) => {
                return `<li class="suggestion-item" data-index="${index}">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="suggestion-main">
                            <strong>${suggestion.displayText}</strong>
                            ${suggestion.details ? `<small class="text-muted ms-2">${suggestion.details}</small>` : ''}
                        </div>
                    </div>
                </li>`;
            })
            .join('');

        this.suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.applySuggestion(this.currentSuggestions[index].text);
            });
        });
    }

    createSuggestionsList() {
        this.suggestionsList = document.createElement('ul');
        this.suggestionsList.className = 'suggestions-list';
        this.input.parentNode.appendChild(this.suggestionsList);
    }

    hideSuggestions() {
        if (this.suggestionsList) {
            this.suggestionsList.style.display = 'none';
            this.currentSuggestions = [];
        }
    }

    handleKeydown(e) {
        if (!this.suggestionsList || this.currentSuggestions.length === 0) return;

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectNextSuggestion();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectPreviousSuggestion();
                break;
            case 'Enter':
            case 'Tab':
                if (this.selectedIndex >= 0) {
                    e.preventDefault();
                    this.applySuggestion(this.currentSuggestions[this.selectedIndex].text);
                }
                break;
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }

    selectNextSuggestion() {
        this.selectedIndex = (this.selectedIndex + 1) % this.currentSuggestions.length;
        this.updateSelection();
    }

    selectPreviousSuggestion() {
        this.selectedIndex = (this.selectedIndex - 1 + this.currentSuggestions.length) % this.currentSuggestions.length;
        this.updateSelection();
    }

    updateSelection() {
        const items = this.suggestionsList.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === this.selectedIndex);
            if (index === this.selectedIndex) {
                item.scrollIntoView({ block: 'nearest' });
            }
        });
    }

    applySuggestion(suggestion) {
        const cursorPosition = this.input.selectionStart;
        const inputValue = this.input.value;
        const beforeCursor = inputValue.substring(0, cursorPosition);
        const afterCursor = inputValue.substring(cursorPosition);
        
        const lastSpaceIndex = beforeCursor.lastIndexOf(' ');
        const start = lastSpaceIndex === -1 ? 0 : lastSpaceIndex + 1;
        
        this.input.value = beforeCursor.substring(0, start) + 
                          suggestion +
                          (afterCursor.startsWith(' ') ? '' : ' ') +
                          afterCursor.trim();
        
        const newPosition = start + suggestion.length + 1;
        this.input.setSelectionRange(newPosition, newPosition);
        this.input.focus();
        
        this.hideSuggestions();
    }
}
