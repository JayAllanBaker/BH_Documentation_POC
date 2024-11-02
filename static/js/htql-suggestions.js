class HTQLSuggestions {
    constructor(input) {
        this.input = input;
        this.suggestionsList = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        
        this.setupEventListeners();
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

    async handleInput() {
        const inputValue = this.input.value;
        console.log('Input value:', inputValue);
        
        try {
            // Check for condition code pattern
            if (inputValue.includes('condition.code')) {
                const parts = inputValue.split('condition.code');
                const searchTerm = parts[1].trim().replace(/^[:.]/, '').trim();
                
                if (searchTerm) {
                    const response = await fetch(`/api/code-suggestions?q=${encodeURIComponent(searchTerm)}`);
                    if (response.ok) {
                        const suggestions = await response.json();
                        this.currentSuggestions = suggestions.map(s => 
                            `condition.code:${s.code} - ${s.description} (${s.system})`
                        );
                        if (this.currentSuggestions.length > 0) {
                            this.showSuggestions();
                        }
                    }
                }
            } else if (inputValue.includes('.') || inputValue.includes(':')) {
                this.generateFieldSuggestions(inputValue);
                if (this.currentSuggestions.length > 0) {
                    this.showSuggestions();
                }
            } else {
                this.hideSuggestions();
            }
        } catch (error) {
            console.error('Error handling input:', error);
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
            
            if (fields[category]) {
                suggestions.push(...fields[category]
                    .filter(f => !field || f.startsWith(field))
                    .map(f => `${category}.${f}`));
            }
        } else if (query.includes(':')) {
            const [field] = query.split(':');
            if (field.includes('gender')) {
                suggestions.push(...['male', 'female', 'other'].map(v => `${field}:${v}`));
            } else if (field.includes('status')) {
                suggestions.push(...['active', 'inactive', 'resolved'].map(v => `${field}:${v}`));
            } else if (field.includes('severity')) {
                suggestions.push(...['mild', 'moderate', 'severe'].map(v => `${field}:${v}`));
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
                let displayText = suggestion;
                if (suggestion.includes(' - ')) {
                    const [code, description] = suggestion.split(' - ');
                    displayText = `<div class="d-flex justify-content-between">
                        <strong>${code}</strong>
                        <small class="text-muted">${description}</small>
                    </div>`;
                }
                return `<li class="suggestion-item" data-index="${index}">${displayText}</li>`;
            })
            .join('');

        // Add click handlers
        this.suggestionsList.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const index = parseInt(item.dataset.index);
                this.applySuggestion(this.currentSuggestions[index]);
            });
        });
    }

    createSuggestionsList() {
        this.suggestionsList = document.createElement('ul');
        this.suggestionsList.className = 'suggestions-list d-none';
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
                    this.applySuggestion(this.currentSuggestions[this.selectedIndex]);
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
        
        // Extract the base suggestion without description
        let value = suggestion;
        if (suggestion.includes(' - ')) {
            value = suggestion.split(' - ')[0].trim();
        }
        
        // Find the last token before cursor
        const lastSpaceIndex = beforeCursor.lastIndexOf(' ');
        const start = lastSpaceIndex === -1 ? 0 : lastSpaceIndex + 1;
        
        // Construct new value
        this.input.value = beforeCursor.substring(0, start) + 
                          value +
                          (afterCursor.startsWith(' ') ? '' : ' ') +
                          afterCursor.trim();
        
        // Position cursor after suggestion
        const newPosition = start + value.length + 1;
        this.input.setSelectionRange(newPosition, newPosition);
        this.input.focus();
        
        this.hideSuggestions();
    }
}
