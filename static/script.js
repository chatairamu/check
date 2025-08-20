// DOM elements
const textInput = document.querySelector('.text-input');
const checkBtn = document.getElementById('check-btn');
const clearBtn = document.getElementById('clear-btn');
const exampleBtn = document.getElementById('example-btn');
const charCount = document.getElementById('char-count');
const wordCount = document.getElementById('word-count');
const issueCount = document.getElementById('issue-count');
const issuesContainer = document.getElementById('issues-container');
const correctedText = document.getElementById('corrected-text');

// Example text for demo
const exampleText = "Hello there! I is a test text to show how our grammar checker works. Hopefully it will find all the error's and help improve you writing. Lets see what it can detected.";

// Initialize
updateStats();

// Event listeners
textInput.addEventListener('input', updateStats);

checkBtn.addEventListener('click', () => {
    const text = textInput.value;
    if (text.trim() === '') {
        return;
    }

    checkBtn.textContent = 'Checking...';
    checkBtn.disabled = true;

    fetch('/check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
    })
    .then(response => response.json())
    .then(data => {
        displayResults(data);
    })
    .catch(error => {
        console.error('Error:', error);
        issuesContainer.innerHTML = '<p class="no-issues">An error occurred. Please try again.</p>';
    })
    .finally(() => {
        checkBtn.textContent = 'Check Grammar';
        checkBtn.disabled = false;
    });
});

clearBtn.addEventListener('click', () => {
    textInput.value = '';
    updateStats();
    issuesContainer.innerHTML = '<p class="no-issues">No issues found. Your text looks good!</p>';
    correctedText.textContent = '';
});

exampleBtn.addEventListener('click', () => {
    textInput.value = exampleText;
    updateStats();
    checkBtn.click();
});

// Functions
function updateStats() {
    const text = textInput.value;
    const characters = text.length;
    const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;

    charCount.textContent = `Characters: ${characters}`;
    wordCount.textContent = `Words: ${words}`;
}

function displayResults(data) {
    // Clear previous results
    issuesContainer.innerHTML = '';

    // Display corrected text
    correctedText.textContent = data.corrected_text;

    // Update issue count
    issueCount.textContent = `Issues found: ${data.issues.length}`;

    if (data.issues.length === 0) {
        issuesContainer.innerHTML = '<p style="text-align: center; padding: 20px;">No issues found. Looks good!</p>';
        return;
    }

    // Create and append each issue element
    data.issues.forEach(issue => {
        const issueElement = document.createElement('div');
        issueElement.classList.add('issue');

        // Create the highlighted context string
        const contextText = issue.context.text;
        const errorOffset = issue.context.offset;
        const errorLength = issue.context.length;
        const before = contextText.substring(0, errorOffset);
        const highlighted = contextText.substring(errorOffset, errorOffset + errorLength);
        const after = contextText.substring(errorOffset + errorLength);
        const contextHTML = `<span>${before}</span><span class="highlight">${highlighted}</span><span>${after}</span>`;

        issueElement.innerHTML = `
            <div class="issue-title">
                <span class="issue-type">${issue.type}</span>
                <span class="issue-suggestion">Suggestion: "${issue.replacements[0] || 'N/A'}"</span>
            </div>
            <p>${issue.message}</p>
            <div class="issue-context">
                ${contextHTML}
            </div>
        `;
        issuesContainer.appendChild(issueElement);
    });
}
