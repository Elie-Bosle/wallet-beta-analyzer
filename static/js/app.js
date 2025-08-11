// Variables globales
let currentWallet = null;
let currentAnalysisId = null;
let statusCheckInterval = null;

// DOM Elements
const walletAddressInput = document.getElementById('wallet-address');
const pasteBtn = document.getElementById('paste-btn');
const validateBtn = document.getElementById('validate-address');
const addressDisplay = document.getElementById('address-display');
const displayAddress = document.getElementById('display-address');
const changeAddressBtn = document.getElementById('change-address');
const analyzeBtn = document.getElementById('analyze-btn');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const resultsDiv = document.getElementById('results');
const errorDiv = document.getElementById('error');

let currentWalletAddress = null;

// Ethereum address validation
function isValidEthereumAddress(address) {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
}

// Function to paste from clipboard
async function pasteFromClipboard() {
    try {
        const text = await navigator.clipboard.readText();
        walletAddressInput.value = text;
        validateAddress();
    } catch (err) {
        console.error('Error pasting:', err);
        showError('Unable to paste from clipboard');
    }
}

// Address validation
function validateAddress() {
    const address = walletAddressInput.value.trim();
    
    if (isValidEthereumAddress(address)) {
        validateBtn.disabled = false;
        validateBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        validateBtn.classList.add('hover:bg-green-600');
        
        // Enable analyze button
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        analyzeBtn.classList.add('hover:from-blue-600', 'hover:to-purple-700');
        
        // Store current address
        currentWalletAddress = address;
    } else {
        validateBtn.disabled = true;
        validateBtn.classList.add('opacity-50', 'cursor-not-allowed');
        validateBtn.classList.remove('hover:bg-green-600');
        
        // Disable analyze button
        analyzeBtn.disabled = true;
        analyzeBtn.classList.add('opacity-50', 'cursor-not-allowed');
        analyzeBtn.classList.remove('hover:from-blue-600', 'hover:to-purple-700');
        
        currentWalletAddress = null;
    }
}

// Confirm address
function confirmAddress() {
    const address = walletAddressInput.value.trim();
    currentWalletAddress = address;
    
    // Display validated address
    displayAddress.textContent = address;
    addressDisplay.classList.remove('hidden');
    
    // Hide input form
    walletAddressInput.parentElement.parentElement.classList.add('hidden');
    validateBtn.classList.add('hidden');
    
    // Enable analyze button
    analyzeBtn.disabled = false;
    analyzeBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    analyzeBtn.classList.add('hover:from-blue-600', 'hover:to-purple-700');
}

// Change address
function changeAddress() {
    currentWalletAddress = null;
    
    // Hide address display
    addressDisplay.classList.add('hidden');
    
    // Show input form
    walletAddressInput.parentElement.parentElement.classList.remove('hidden');
    validateBtn.classList.remove('hidden');
    
    // Clear field
    walletAddressInput.value = '';
    validateAddress();
    
    // Disable analyze button
    analyzeBtn.disabled = true;
    analyzeBtn.classList.add('opacity-50', 'cursor-not-allowed');
    analyzeBtn.classList.remove('hover:from-blue-600', 'hover:to-purple-700');
    
    // Hide results
    resultsDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
}

// Event listeners
walletAddressInput.addEventListener('input', validateAddress);
walletAddressInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter' && !validateBtn.disabled) {
        confirmAddress();
    }
});

pasteBtn.addEventListener('click', pasteFromClipboard);
validateBtn.addEventListener('click', confirmAddress);
changeAddressBtn.addEventListener('click', changeAddress);

// AI Wallet analysis
analyzeBtn.addEventListener('click', async function() {
    if (!currentWalletAddress) {
        showError('No wallet address selected');
        return;
    }
    
    // Hide previous results
    resultsDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    
    // Show progress bar
    progressBar.classList.remove('hidden');
    analyzeBtn.disabled = true;
    
    try {
        // Start AI analysis
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                wallet_address: currentWalletAddress
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        
        const data = await response.json();
        const analysisId = data.analysis_id;
        
        // Polling for AI results
        await pollResults(analysisId);
        
    } catch (error) {
        console.error('AI Analysis error:', error);
        showError('AI Analysis error: ' + error.message);
        progressBar.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
});

// Results polling
async function pollResults(analysisId) {
    const maxAttempts = 60; // 60 seconds max
    let attempts = 0;
    
    const poll = async () => {
        try {
            const response = await fetch(`/api/status/${analysisId}`);
            const data = await response.json();
            
            if (data.status === 'completed') {
                // AI Analysis completed
                progressBar.classList.add('hidden');
                analyzeBtn.disabled = false;
                displayResults(data.result);
                return;
            } else if (data.status === 'error') {
                // Error
                progressBar.classList.add('hidden');
                analyzeBtn.disabled = false;
                showError('AI Analysis error: ' + data.error);
                return;
            } else {
                // In progress
                attempts++;
                if (attempts >= maxAttempts) {
                    progressBar.classList.add('hidden');
                    analyzeBtn.disabled = false;
                    showError('Timeout - AI analysis is taking too long');
                    return;
                }
                
                // Update progress
                const progress = Math.min((attempts / maxAttempts) * 100, 95);
                document.getElementById('progress-fill').style.width = progress + '%';
                progressText.textContent = `AI is analyzing your portfolio... (${Math.round(progress)}%)`;
                
                // Continue polling
                setTimeout(poll, 1000);
            }
        } catch (error) {
            progressBar.classList.add('hidden');
            analyzeBtn.disabled = false;
            showError('Error retrieving AI results');
        }
    };
    
    poll();
}

// Display errors
function showError(message) {
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

// Display results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const scoreValue = document.getElementById('score-value');
    const totalValue = document.getElementById('total-value');
    const tokenCount = document.getElementById('token-count');
    const chainCount = document.getElementById('chain-count');
    const tokensByChain = document.getElementById('tokens-by-chain');

    // Display AI score
    const score = data.score.score;
    scoreValue.textContent = score.toFixed(1);
    
    // Color score based on value
    if (score >= 80) {
        scoreValue.className = 'text-3xl font-bold text-green-600';
    } else if (score >= 60) {
        scoreValue.className = 'text-3xl font-bold text-yellow-600';
    } else if (score >= 40) {
        scoreValue.className = 'text-3xl font-bold text-orange-600';
    } else {
        scoreValue.className = 'text-3xl font-bold text-red-600';
    }

    // Display statistics
    totalValue.textContent = `$${data.total_value.toFixed(2)}`;
    tokenCount.textContent = data.token_count;
    
    // Count unique chains
    const chains = [...new Set(data.tokens.map(token => token.chain))];
    chainCount.textContent = chains.length;

    // Group tokens by chain
    const tokensByChainMap = {};
    data.tokens.forEach(token => {
        if (!tokensByChainMap[token.chain]) {
            tokensByChainMap[token.chain] = [];
        }
        tokensByChainMap[token.chain].push(token);
    });

    // Display tokens by chain
    tokensByChain.innerHTML = '';
    Object.keys(tokensByChainMap).forEach(chain => {
        const chainTokens = tokensByChainMap[chain];
        const chainValue = chainTokens.reduce((sum, token) => sum + token.usd, 0);
        
        const chainDiv = document.createElement('div');
        chainDiv.className = 'bg-gray-50 rounded-lg p-4';
        chainDiv.innerHTML = `
            <h4 class="text-lg font-semibold text-gray-800 mb-3">${chain} ($${chainValue.toFixed(2)})</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                ${chainTokens.map(token => `
                    <div class="bg-white rounded-lg p-3 border border-gray-200">
                        <div class="flex justify-between items-center">
                            <div>
                                <div class="font-semibold text-gray-800">${token.sym}</div>
                                <div class="text-sm text-gray-600">$${token.usd.toFixed(2)}</div>
                            </div>
                            <div class="text-right">
                                <div class="text-xs text-gray-500">${token.addr.substring(0, 8)}...</div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        tokensByChain.appendChild(chainDiv);
    });

    resultsDiv.classList.remove('hidden');
}

// Initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initial validation
    validateAddress();
});
