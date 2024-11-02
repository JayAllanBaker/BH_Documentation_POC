[Previous htql-suggestions.js content with updated showSuggestions method]

showSuggestions() {
    if (!this.suggestionsList) {
        this.createSuggestionsList();
    }

    this.selectedIndex = -1;
    this.suggestionsList.style.display = 'block';
    
    this.suggestionsList.innerHTML = this.currentSuggestions
        .map((suggestion, index) => {
            const [code, description] = suggestion.split(' - ');
            return `
                <li class="suggestion-item" data-index="${index}">
                    <div class="d-flex justify-content-between">
                        <strong>${code}</strong>
                        <small class="text-muted">${description}</small>
                    </div>
                </li>
            `;
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
