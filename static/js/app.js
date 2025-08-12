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

    // Generate AI insights and recommendations
    const aiInsights = generateAIInsights(data, score);
    
    // Display AI insights instead of token details
    tokensByChain.innerHTML = `
        <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
            <h4 class="text-xl font-semibold text-gray-800 mb-4">
                <i class="fas fa-brain mr-2 text-purple-600"></i>
                AI Portfolio Analysis
            </h4>
            <p class="text-gray-700 mb-4">${aiInsights.analysis}</p>
        </div>
        
        <div class="bg-green-50 rounded-lg p-6">
            <h4 class="text-lg font-semibold text-green-800 mb-4">
                <i class="fas fa-lightbulb mr-2 text-green-600"></i>
                AI Recommendations
            </h4>
            <ul class="space-y-3">
                ${aiInsights.recommendations.map(rec => `
                    <li class="flex items-start">
                        <i class="fas fa-arrow-right text-green-600 mt-1 mr-3 flex-shrink-0"></i>
                        <span class="text-green-700">${rec}</span>
                    </li>
                `).join('')}
            </ul>
        </div>
    `;

    resultsDiv.classList.remove('hidden');
}

// Generate AI insights based on portfolio data
function generateAIInsights(data, score) {
    const totalValue = data.total_value;
    const tokenCount = data.token_count;
    const chains = [...new Set(data.tokens.map(token => token.chain))];
    
    // Analyze portfolio composition
    const stableTokens = data.tokens.filter(token => 
        ['USDC', 'USDT', 'DAI', 'ETH', 'WETH', 'WBTC'].includes(token.sym.toUpperCase())
    );
    const stableValue = stableTokens.reduce((sum, token) => sum + token.usd, 0);
    const stablePercentage = (stableValue / totalValue) * 100;
    
    // Analyze diversification
    const highValueTokens = data.tokens.filter(token => token.usd > totalValue * 0.1);
    const isConcentrated = highValueTokens.length > 0;
    
    // Generate analysis
    let analysis = "";
    if (score >= 80) {
        analysis = "🤖 Excellent portfolio stability detected! Your AI analysis shows a well-balanced portfolio with strong diversification and risk management. The combination of stable assets and strategic token selection demonstrates sophisticated portfolio construction.";
    } else if (score >= 60) {
        analysis = "🤖 Good portfolio foundation with room for optimization. Our AI analysis indicates moderate stability with some areas for improvement. The portfolio shows basic diversification but could benefit from enhanced risk management strategies.";
    } else if (score >= 40) {
        analysis = "🤖 Moderate portfolio risk detected. AI analysis reveals several areas requiring attention for improved stability. The current composition suggests higher volatility exposure that could be mitigated through strategic rebalancing.";
    } else {
        analysis = "🤖 High portfolio volatility detected. Our AI analysis indicates significant risk exposure requiring immediate attention. The current composition suggests aggressive positioning that may benefit from defensive strategies.";
    }
    
    // Generate recommendations
    const recommendations = [];
    
    if (stablePercentage < 30) {
        recommendations.push("Increase stablecoin allocation to at least 30% for better risk management during market volatility");
    }
    
    if (isConcentrated) {
        recommendations.push("Reduce concentration in high-value positions to improve diversification and minimize single-token risk");
    }
    
    if (tokenCount < 10) {
        recommendations.push("Consider adding more diverse tokens across different sectors to enhance portfolio resilience");
    }
    
    if (chains.length < 3) {
        recommendations.push("Expand across more blockchain networks to reduce platform-specific risks and capture cross-chain opportunities");
    }
    
    if (score < 60) {
        recommendations.push("Implement a more conservative allocation strategy focusing on established projects with proven track records");
    }
    
    // Add general recommendations if not enough specific ones
    if (recommendations.length < 2) {
        if (score < 70) {
            recommendations.push("Consider rebalancing quarterly to maintain optimal risk-adjusted returns");
        }
        recommendations.push("Monitor portfolio performance regularly and adjust strategy based on market conditions");
    }
    
    // Limit to 3 recommendations
    return {
        analysis: analysis,
        recommendations: recommendations.slice(0, 3)
    };
}

// Initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initial validation
    validateAddress();
});
