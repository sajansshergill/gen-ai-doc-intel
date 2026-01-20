// GenAI Document Intelligence Platform - Frontend Application
// API Base URL - defaults to same origin, can be overridden via window.API_BASE_URL
const API_BASE = window.API_BASE_URL || window.location.origin;

// State
let stats = {
    totalDocs: 0,
    totalChunks: 0,
    totalQueries: 0,
    avgConfidence: 0
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupFileUpload();
    loadDocuments();
    loadStats();
    
    // Auto-refresh stats every 30 seconds
    setInterval(loadStats, 30000);
});

// File Upload
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#1a73e8';
        uploadArea.style.background = '#e8f0fe';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '';
        uploadArea.style.background = '';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '';
        uploadArea.style.background = '';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const progressContainer = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const uploadResult = document.getElementById('uploadResult');
    
    progressContainer.style.display = 'block';
    uploadResult.innerHTML = '';
    
    // Log for debugging
    console.log('Starting upload...');
    console.log('API_BASE:', API_BASE);
    console.log('File:', file.name, file.size, 'bytes');
    
    try {
        progressText.textContent = 'Uploading...';
        progressFill.style.width = '30%';
        
        const uploadUrl = `${API_BASE}/v1/documents`;
        console.log('Upload URL:', uploadUrl);
        
        const response = await fetch(uploadUrl, {
            method: 'POST',
            body: formData,
            // Don't set Content-Type - let browser set it with boundary
        });
        
        console.log('Response status:', response.status, response.statusText);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        progressFill.style.width = '70%';
        progressText.textContent = 'Processing...';
        
        if (!response.ok) {
            // Try to get error details from response
            let errorDetail = `${response.status} ${response.statusText}`;
            let errorBody = '';
            try {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorData.message || errorDetail;
                    errorBody = JSON.stringify(errorData, null, 2);
                } else {
                    errorBody = await response.text();
                    if (errorBody) {
                        errorDetail = errorBody.substring(0, 200);
                    }
                }
            } catch (e) {
                console.error('Error reading response:', e);
            }
            
            console.error('Upload failed:', errorDetail);
            console.error('Response body:', errorBody);
            throw new Error(`Upload failed: ${errorDetail}`);
        }
        
        const result = await response.json();
        console.log('Upload success:', result);
        
        progressFill.style.width = '100%';
        progressText.textContent = 'Complete!';
        
        setTimeout(() => {
            progressContainer.style.display = 'none';
            progressFill.style.width = '0%';
        }, 1000);
        
        uploadResult.innerHTML = `
            <div style="background: #e8f5e9; border-left: 4px solid #4caf50; padding: 1rem; border-radius: 8px;">
                <h4 style="color: #2e7d32; margin: 0 0 0.5rem 0;">✅ Document Uploaded Successfully</h4>
                <p style="margin: 0.25rem 0;"><strong>Document ID:</strong> ${result.doc_id}</p>
                <p style="margin: 0.25rem 0;"><strong>Filename:</strong> ${result.filename}</p>
                <p style="margin: 0.25rem 0;"><strong>Status:</strong> ${result.status}</p>
                <p style="margin: 0.25rem 0;"><strong>Message:</strong> ${result.message || 'Processing in background...'}</p>
            </div>
        `;
        
        loadDocuments();
        loadStats();
    } catch (error) {
        progressContainer.style.display = 'none';
        console.error('Upload error details:', error);
        console.error('Error name:', error.name);
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
        
        const errorMsg = error.message || 'Unknown error';
        const isNetworkError = errorMsg.includes('Failed to fetch') || 
                               errorMsg.includes('NetworkError') || 
                               errorMsg.includes('Network request failed') ||
                               error.name === 'TypeError' ||
                               error.name === 'NetworkError';
        
        let diagnosticInfo = '';
        if (isNetworkError) {
            diagnosticInfo = `
                <div style="margin-top: 1rem; padding: 0.75rem; background: #fff3cd; border-radius: 4px; font-size: 0.85rem;">
                    <strong>🔍 Diagnostic Info:</strong><br>
                    API URL: ${API_BASE}<br>
                    Error Type: ${error.name}<br>
                    <br>
                    <strong>Possible causes:</strong><br>
                    • Backend not running (check Render dashboard)<br>
                    • CORS issue (backend should allow GitHub Pages origin)<br>
                    • Network connectivity issue<br>
                    <br>
                    <strong>Test backend:</strong><br>
                    <code style="background: #f5f5f5; padding: 0.25rem 0.5rem; border-radius: 3px;">
                        curl ${API_BASE}/health
                    </code>
                </div>
            `;
        }
        
        uploadResult.innerHTML = `
            <div style="background: #ffebee; border-left: 4px solid #ea4335; padding: 1rem; border-radius: 8px;">
                <h4 style="color: #ea4335; margin: 0 0 0.5rem 0;">❌ Upload Failed</h4>
                <p style="margin: 0 0 0.5rem 0; font-weight: 500;">${errorMsg}</p>
                <p style="margin: 0; font-size: 0.85rem; color: #666;">
                    Check browser console (F12) for detailed error information.
                </p>
                ${diagnosticInfo}
            </div>
        `;
    }
}

// Load Documents
async function loadDocuments() {
    const documentList = document.getElementById('documentList');
    documentList.innerHTML = '<div class="loading">Loading documents...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/v1/documents`);
        
        if (!response.ok) {
            if (response.status === 404 || response.status === 0) {
                throw new Error('Backend API not available. Please deploy the backend API or configure API_BASE_URL.');
            }
            throw new Error(`API error: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Handle case where API returns error format
        if (data.error || data.detail) {
            throw new Error(data.error || data.detail || 'Unknown API error');
        }
        
        if (!data.documents || data.documents.length === 0) {
            documentList.innerHTML = '<div class="loading">No documents uploaded yet. Upload your first document above!</div>';
            return;
        }
        
        documentList.innerHTML = data.documents.map(doc => `
            <div class="document-item">
                <div class="document-info">
                    <h4>${doc.filename}</h4>
                    <p>${doc.pages} pages • ${doc.chunks} chunks • Uploaded ${new Date(doc.uploaded_at).toLocaleDateString()}</p>
                </div>
                <div class="document-actions">
                    <button class="btn-secondary" onclick="viewDocument('${doc.doc_id}')">View</button>
                </div>
            </div>
        `).join('');
        
        stats.totalDocs = data.documents.length;
        updateStats();
    } catch (error) {
        console.error('Error loading documents:', error);
        const errorMsg = error.message || 'Unknown error';
        documentList.innerHTML = `
            <div style="padding: 1rem; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
                <h4 style="margin: 0 0 0.5rem 0; color: #856404;">⚠️ Backend API Not Available</h4>
                <p style="margin: 0; color: #856404; font-size: 0.9rem;">${errorMsg}</p>
                <p style="margin: 0.5rem 0 0 0; color: #856404; font-size: 0.85rem;">
                    <strong>Current API URL:</strong> ${API_BASE}<br>
                    <strong>Solution:</strong> Deploy the backend API (see DEPLOYMENT.md) or set API_BASE_URL secret in GitHub.
                </p>
            </div>
        `;
    }
}

// Query Documents
async function executeQuery() {
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();
    const useLLM = document.getElementById('useLLM').checked;
    const topK = parseInt(document.getElementById('topKSelect').value);
    
    if (!query) {
        alert('Please enter a question');
        return;
    }
    
    const resultsCard = document.getElementById('resultsCard');
    const resultsContainer = document.getElementById('queryResults');
    const evaluationCard = document.getElementById('evaluationCard');
    
    resultsContainer.innerHTML = '<div class="loading">Searching documents...</div>';
    resultsCard.style.display = 'block';
    evaluationCard.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/v1/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                question: query,
                top_k: topK,
                use_llm: useLLM
            })
        });
        
        const result = await response.json();
        
        // Display results
        const confidence = (result.confidence * 100).toFixed(1);
        document.getElementById('confidenceBadge').textContent = `${confidence}% Confidence`;
        
        resultsContainer.innerHTML = `
            <div class="result-item">
                <h4>Answer</h4>
                <p>${result.answer}</p>
            </div>
            ${result.evidence.map(ev => `
                <div class="result-item">
                    <h4>${ev.filename || 'Document'} - Page ${ev.page}</h4>
                    <p>${ev.snippet}</p>
                    <div class="result-meta">
                        <span>Score: ${(ev.score * 100).toFixed(1)}%</span>
                        <span>Chunk ID: ${ev.chunk_id}</span>
                    </div>
                </div>
            `).join('')}
        `;
        
        // Show evaluation
        if (result.citations && result.citations.length > 0) {
            showEvaluation(result);
        }
        
        stats.totalQueries++;
        stats.avgConfidence = ((stats.avgConfidence * (stats.totalQueries - 1)) + result.confidence) / stats.totalQueries;
        updateStats();
    } catch (error) {
        resultsContainer.innerHTML = `<div class="loading">Error: ${error.message}</div>`;
    }
}

// Evaluation Display
function showEvaluation(result) {
    const evaluationCard = document.getElementById('evaluationCard');
    const evaluationResults = document.getElementById('evaluationResults');
    
    const citationCount = result.citations.length;
    const avgScore = result.evidence.reduce((sum, e) => sum + e.score, 0) / result.evidence.length;
    
    evaluationResults.innerHTML = `
        <div class="evaluation-container">
            <div class="eval-metric">
                <div class="eval-metric-value">${citationCount}</div>
                <div class="eval-metric-label">Citations</div>
            </div>
            <div class="eval-metric">
                <div class="eval-metric-value">${(avgScore * 100).toFixed(1)}%</div>
                <div class="eval-metric-label">Avg Relevance</div>
            </div>
            <div class="eval-metric">
                <div class="eval-metric-value">${result.evidence.length}</div>
                <div class="eval-metric-label">Evidence Chunks</div>
            </div>
            <div class="eval-metric">
                <div class="eval-metric-value">${(result.confidence * 100).toFixed(1)}%</div>
                <div class="eval-metric-label">Confidence</div>
            </div>
        </div>
    `;
    
    evaluationCard.style.display = 'block';
}

// View Document
async function viewDocument(docId) {
    try {
        const [docResponse, chunksResponse, tablesResponse] = await Promise.all([
            fetch(`${API_BASE}/v1/documents/${docId}`),
            fetch(`${API_BASE}/v1/documents/${docId}/chunks`),
            fetch(`${API_BASE}/v1/documents/${docId}/tables`)
        ]);
        
        const doc = await docResponse.json();
        const chunks = await chunksResponse.json();
        const tables = await tablesResponse.json();
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5); z-index: 1000;
            display: flex; align-items: center; justify-content: center;
            padding: 2rem;
        `;
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 12px; max-width: 800px; max-height: 90vh; overflow-y: auto; padding: 2rem; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem;">
                    <h2>${doc.filename}</h2>
                    <button onclick="this.closest('div[style*=\"position: fixed\"]').remove()" style="background: none; border: none; font-size: 1.5rem; cursor: pointer;">×</button>
                </div>
                <div style="margin-bottom: 1.5rem;">
                    <p><strong>Pages:</strong> ${doc.pages}</p>
                    <p><strong>Chunks:</strong> ${doc.chunks}</p>
                    <p><strong>Extraction Method:</strong> ${doc.extraction_method}</p>
                </div>
                <div style="margin-bottom: 1.5rem;">
                    <h3>Chunks (${chunks.total})</h3>
                    <div style="max-height: 300px; overflow-y: auto;">
                        ${chunks.chunks.map(c => `
                            <div style="padding: 0.75rem; margin-bottom: 0.5rem; background: #f8f9fa; border-radius: 6px;">
                                <strong>Page ${c.page}</strong> - ${c.char_count} chars
                                <p style="font-size: 0.875rem; margin-top: 0.25rem; color: #5f6368;">${c.text}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ${tables.total > 0 ? `
                    <div>
                        <h3>Tables (${tables.total})</h3>
                        <p>${tables.total} table(s) extracted from this document.</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    } catch (error) {
        alert(`Error loading document: ${error.message}`);
    }
}

// Load Stats
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/v1/documents`);
        const data = await response.json();
        
        let totalChunks = 0;
        data.documents.forEach(doc => {
            totalChunks += doc.chunks || 0;
        });
        
        stats.totalDocs = data.documents.length;
        stats.totalChunks = totalChunks;
        updateStats();
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStats() {
    document.getElementById('totalDocs').textContent = stats.totalDocs;
    document.getElementById('totalChunks').textContent = stats.totalChunks;
    document.getElementById('totalQueries').textContent = stats.totalQueries;
    document.getElementById('avgConfidence').textContent = `${(stats.avgConfidence * 100).toFixed(0)}%`;
}

// Enter key to query
document.getElementById('queryInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && e.ctrlKey) {
        executeQuery();
    }
});
