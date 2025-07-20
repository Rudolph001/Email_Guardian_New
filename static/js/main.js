// Email Guardian - Main JavaScript File

// Global variables
let currentSessionId = null;
let loadingOverlay = null;

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
});

function initializeApplication() {
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize file upload
    initializeFileUpload();
    
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Initialize DataTables if available
    if (typeof DataTable !== 'undefined') {
        initializeDataTables();
    }
    
    // Set up event listeners
    setupEventListeners();
    
    // Load session-specific content if on dashboard pages
    const sessionId = extractSessionIdFromUrl();
    if (sessionId) {
        currentSessionId = sessionId;
        loadSessionContent();
    }
}

function extractSessionIdFromUrl() {
    const path = window.location.pathname;
    const matches = path.match(/\/(dashboard|cases|escalations|sender_analysis|time_analysis|whitelist_analysis|advanced_ml_dashboard)\/([^/]+)/);
    return matches ? matches[2] : null;
}

function setupEventListeners() {
    // Case management
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('view-case-btn')) {
            const recordId = e.target.dataset.recordId;
            showCaseDetails(currentSessionId, recordId);
        }
        
        if (e.target.classList.contains('escalate-case-btn')) {
            const recordId = e.target.dataset.recordId;
            escalateCase(currentSessionId, recordId);
        }
        
        if (e.target.classList.contains('update-case-status-btn')) {
            const recordId = e.target.dataset.recordId;
            const newStatus = e.target.dataset.newStatus;
            updateCaseStatus(currentSessionId, recordId, newStatus);
        }
        
        if (e.target.classList.contains('generate-email-btn')) {
            const recordId = e.target.dataset.recordId;
            generateEscalationEmail(currentSessionId, recordId);
        }
    });
    
    // Filter form submission
    const filterForm = document.getElementById('filterForm');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyFilters();
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            applyFilters();
        }, 500));
    }
    
    // Auto-refresh for processing status
    if (document.querySelector('.processing-status.processing')) {
        setInterval(checkProcessingStatus, 5000);
    }
}

function initializeFileUpload() {
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('fileInput');
    
    if (!fileUploadArea || !fileInput) return;
    
    // Click to upload
    fileUploadArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    // File selection
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            displaySelectedFile(this.files[0]);
        }
    });
    
    // Drag and drop
    fileUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });
    
    fileUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });
    
    fileUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            displaySelectedFile(files[0]);
        }
    });
}

function displaySelectedFile(file) {
    const fileInfo = document.getElementById('fileInfo');
    const uploadBtn = document.getElementById('uploadBtn');
    
    if (fileInfo && uploadBtn) {
        fileInfo.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-file-csv"></i>
                <strong>Selected:</strong> ${file.name} (${formatFileSize(file.size)})
            </div>
        `;
        uploadBtn.disabled = false;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function loadSessionContent() {
    if (!currentSessionId) return;
    
    // Load ML insights for dashboard
    if (document.getElementById('mlInsightsChart')) {
        loadMLInsights(currentSessionId);
    }
    
    // Load BAU analysis
    if (document.getElementById('bauAnalysisChart')) {
        loadBAUAnalysis(currentSessionId);
    }
    
    // Load attachment analytics
    if (document.getElementById('attachmentRiskChart')) {
        loadAttachmentRiskAnalytics(currentSessionId);
    }
    
    // Load sender analysis
    if (document.getElementById('senderBehaviorChart')) {
        loadSenderAnalysis(currentSessionId);
    }
    
    // Load time analysis
    if (document.getElementById('timePatternChart')) {
        loadTimeAnalysis(currentSessionId);
    }
    
    // Load whitelist analysis
    if (document.getElementById('whitelistRecommendationsChart')) {
        loadWhitelistAnalysis(currentSessionId);
    }
}

// API Functions
async function loadMLInsights(sessionId) {
    try {
        showLoading('Loading ML insights...');
        const response = await fetch(`/api/ml_insights/${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            console.warn('ML insights error:', data.error);
            // Still update display with default/available data
            updateMLInsightsDisplay(data);
        } else {
            updateMLInsightsDisplay(data);
        }
        
        hideLoading();
    } catch (error) {
        console.error('Error loading ML insights:', error);
        showError('Failed to load ML insights: ' + error.message);
        
        // Provide fallback data
        updateMLInsightsDisplay({
            total_records: 0,
            analyzed_records: 0,
            risk_distribution: {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0},
            average_risk_score: 0.0,
            processing_complete: false,
            error: 'Failed to load data'
        });
        
        hideLoading();
    }
}

async function loadBAUAnalysis(sessionId) {
    try {
        const response = await fetch(`/api/bau_analysis/${sessionId}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('BAU analysis error:', data.error);
            return;
        }
        
        updateBAUAnalysisDisplay(data);
    } catch (error) {
        console.error('Error loading BAU analysis:', error);
    }
}

async function loadAttachmentRiskAnalytics(sessionId) {
    try {
        const response = await fetch(`/api/attachment_risk_analytics/${sessionId}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('Attachment risk analytics error:', data.error);
            return;
        }
        
        updateAttachmentRiskDisplay(data);
    } catch (error) {
        console.error('Error loading attachment risk analytics:', error);
    }
}

async function showCaseDetails(sessionId, recordId) {
    try {
        showLoading('Loading case details...');
        const response = await fetch(`/api/case/${sessionId}/${recordId}`);
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to load case details: ' + data.error);
            return;
        }
        
        displayCaseDetailsModal(data);
        hideLoading();
    } catch (error) {
        console.error('Error loading case details:', error);
        showError('Failed to load case details');
        hideLoading();
    }
}

async function updateCaseStatus(sessionId, recordId, newStatus) {
    try {
        const response = await fetch(`/api/case/${sessionId}/${recordId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: newStatus,
                notes: `Status changed to ${newStatus} by user`
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            showError('Failed to update case status: ' + result.error);
            return;
        }
        
        showSuccess(`Case status updated to ${newStatus}`);
        
        // Refresh the page or update the UI
        setTimeout(() => {
            location.reload();
        }, 1500);
        
    } catch (error) {
        console.error('Error updating case status:', error);
        showError('Failed to update case status');
    }
}

async function escalateCase(sessionId, recordId) {
    try {
        const result = await updateCaseStatus(sessionId, recordId, 'Escalated');
        
        if (result !== false) {
            // Show escalation options modal
            showEscalationModal(sessionId, recordId);
        }
    } catch (error) {
        console.error('Error escalating case:', error);
        showError('Failed to escalate case');
    }
}

async function generateEscalationEmail(sessionId, recordId) {
    try {
        showLoading('Generating email...');
        const response = await fetch(`/api/escalation/${sessionId}/${recordId}/generate-email`);
        const data = await response.json();
        
        if (data.error) {
            showError('Failed to generate email: ' + data.error);
            return;
        }
        
        displayEmailDraftModal(data);
        hideLoading();
    } catch (error) {
        console.error('Error generating email:', error);
        showError('Failed to generate email');
        hideLoading();
    }
}

async function sendEscalationEmail(sessionId, recordId, emailData) {
    try {
        showLoading('Sending email...');
        const response = await fetch(`/api/escalation/${sessionId}/${recordId}/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emailData)
        });
        
        const result = await response.json();
        
        if (result.error) {
            showError('Failed to send email: ' + result.error);
            return;
        }
        
        showSuccess('Email sent successfully');
        hideLoading();
        
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('emailDraftModal'));
        if (modal) {
            modal.hide();
        }
        
    } catch (error) {
        console.error('Error sending email:', error);
        showError('Failed to send email');
        hideLoading();
    }
}

function openOutlookDraft(emailContent) {
    const mailtoUrl = `mailto:${emailContent.to}?subject=${encodeURIComponent(emailContent.subject)}&body=${encodeURIComponent(emailContent.body)}`;
    window.open(mailtoUrl);
}

async function loadSenderAnalysis(sessionId) {
    try {
        const response = await fetch(`/api/sender_analysis/${sessionId}`);
        const data = await response.json();
        updateSenderAnalysisDisplay(data);
    } catch (error) {
        console.error('Error loading sender analysis:', error);
    }
}

async function loadTimeAnalysis(sessionId) {
    try {
        const response = await fetch(`/api/time_analysis/${sessionId}`);
        const data = await response.json();
        updateTimeAnalysisDisplay(data);
    } catch (error) {
        console.error('Error loading time analysis:', error);
    }
}

async function loadWhitelistAnalysis(sessionId) {
    try {
        const response = await fetch(`/api/whitelist_analysis/${sessionId}`);
        const data = await response.json();
        updateWhitelistAnalysisDisplay(data);
    } catch (error) {
        console.error('Error loading whitelist analysis:', error);
    }
}

// Display Functions
function updateMLInsightsDisplay(data) {
    // Update statistics with safe fallbacks
    const totalRecords = document.getElementById('totalRecords');
    const analyzedRecords = document.getElementById('analyzedRecords');
    const avgRiskScore = document.getElementById('avgRiskScore');
    
    if (totalRecords) totalRecords.textContent = data.total_records || 0;
    if (analyzedRecords) analyzedRecords.textContent = data.analyzed_records || 0;
    if (avgRiskScore) avgRiskScore.textContent = (data.average_risk_score || 0).toFixed(3);
    
    // Update risk distribution chart with safe fallbacks
    const riskDistribution = data.risk_distribution || {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0};
    const chartElement = document.getElementById('mlInsightsChart');
    
    if (chartElement) {
        try {
            createRiskDistributionChart(riskDistribution);
        } catch (error) {
            console.error('Error creating risk distribution chart:', error);
        }
    }
    
    // Show error message if present
    if (data.error) {
        console.warn('ML Insights warning:', data.error);
    }
}

function updateBAUAnalysisDisplay(data) {
    if (!data || data.error) return;
    
    // Update BAU statistics
    const bauScore = document.getElementById('bauScore');
    const highVolumeComms = document.getElementById('highVolumeComms');
    
    if (bauScore) bauScore.textContent = (data.bau_statistics?.bau_score || 0).toFixed(1);
    if (highVolumeComms) highVolumeComms.textContent = data.high_volume_pairs ? Object.keys(data.high_volume_pairs).length : 0;
    
    // Create charts if elements exist
    if (document.getElementById('bauAnalysisChart')) {
        createBAUChart(data);
    }
}

function updateAttachmentRiskDisplay(data) {
    if (!data || data.error) return;
    
    // Update attachment statistics
    const totalAttachments = document.getElementById('totalAttachments');
    const highRiskAttachments = document.getElementById('highRiskAttachments');
    
    if (totalAttachments) totalAttachments.textContent = data.total_attachments || 0;
    if (highRiskAttachments) highRiskAttachments.textContent = data.risk_distribution?.high_risk_count || 0;
    
    // Create attachment risk chart
    if (document.getElementById('attachmentRiskChart')) {
        createAttachmentRiskChart(data);
    }
}

function updateSenderAnalysisDisplay(data) {
    if (!data || data.error) return;
    
    const totalSenders = document.getElementById('totalSenders');
    const highRiskSenders = document.getElementById('highRiskSenders');
    
    if (totalSenders) totalSenders.textContent = data.total_senders || 0;
    if (highRiskSenders) highRiskSenders.textContent = data.summary_statistics?.high_risk_senders || 0;
    
    if (document.getElementById('senderBehaviorChart')) {
        createSenderBehaviorChart(data);
    }
}

function updateTimeAnalysisDisplay(data) {
    if (!data || data.error) return;
    
    const businessHoursRatio = document.getElementById('businessHoursRatio');
    const afterHoursActivity = document.getElementById('afterHoursActivity');
    
    if (businessHoursRatio) businessHoursRatio.textContent = ((data.business_hours_ratio || 0) * 100).toFixed(1) + '%';
    if (afterHoursActivity) afterHoursActivity.textContent = data.after_hours_activity || 0;
    
    if (document.getElementById('timePatternChart')) {
        createTimePatternChart(data);
    }
}

function updateWhitelistAnalysisDisplay(data) {
    if (!data || data.error) return;
    
    const recommendedDomains = document.getElementById('recommendedDomains');
    const whitelistCoverage = document.getElementById('whitelistCoverage');
    
    if (recommendedDomains) recommendedDomains.textContent = data.whitelist_recommendations?.length || 0;
    if (whitelistCoverage) whitelistCoverage.textContent = data.whitelist_effectiveness?.whitelist_ratio || 0;
    
    if (document.getElementById('whitelistRecommendationsChart')) {
        createWhitelistChart(data);
    }
}

function displayCaseDetailsModal(caseData) {
    const modalHtml = `
        <div class="modal fade" id="caseDetailsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Case Details - ${caseData.record_id}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Email Information</h6>
                                <p><strong>Sender:</strong> ${caseData.sender || 'N/A'}</p>
                                <p><strong>Recipients:</strong> ${caseData.recipients || 'N/A'}</p>
                                <p><strong>Domain:</strong> ${caseData.recipients_email_domain || 'N/A'}</p>
                                <p><strong>Subject:</strong> ${caseData.subject || 'N/A'}</p>
                                <p><strong>Time:</strong> ${caseData.time || 'N/A'}</p>
                            </div>
                            <div class="col-md-6">
                                <h6>Risk Assessment</h6>
                                <p><strong>Risk Level:</strong> <span class="risk-${caseData.risk_level?.toLowerCase() || 'low'}">${caseData.risk_level || 'Low'}</span></p>
                                <p><strong>ML Risk Score:</strong> ${(caseData.ml_risk_score || 0).toFixed(3)}</p>
                                <p><strong>Case Status:</strong> <span class="badge status-${caseData.case_status?.toLowerCase() || 'active'}">${caseData.case_status || 'Active'}</span></p>
                            </div>
                        </div>
                        <hr>
                        <div class="row">
                            <div class="col-12">
                                <h6>Attachments</h6>
                                <p>${caseData.attachments || 'No attachments'}</p>
                                <h6>ML Explanation</h6>
                                <p>${caseData.ml_explanation || 'No explanation available'}</p>
                                <h6>Justification</h6>
                                <p>${caseData.justification || 'No justification provided'}</p>
                            </div>
                        </div>
                        ${caseData.rule_matches && caseData.rule_matches.length > 0 ? `
                            <hr>
                            <h6>Rule Matches</h6>
                            <ul class="list-group">
                                ${caseData.rule_matches.map(rule => `
                                    <li class="list-group-item">
                                        <strong>${rule.rule_name}</strong>: ${rule.description || 'No description'}
                                        <span class="badge bg-primary">Priority: ${rule.priority}</span>
                                    </li>
                                `).join('')}
                            </ul>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-warning update-case-status-btn" data-record-id="${caseData.record_id}" data-new-status="Cleared">Clear Case</button>
                        <button type="button" class="btn btn-danger escalate-case-btn" data-record-id="${caseData.record_id}">Escalate</button>
                        <button type="button" class="btn btn-primary generate-email-btn" data-record-id="${caseData.record_id}">Generate Email</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal
    const existingModal = document.getElementById('caseDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('caseDetailsModal'));
    modal.show();
}

function displayEmailDraftModal(emailData) {
    const modalHtml = `
        <div class="modal fade" id="emailDraftModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Escalation Email Draft</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="emailDraftForm">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">To:</label>
                                        <input type="email" class="form-control" name="to" value="${emailData.to || ''}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">CC:</label>
                                        <input type="email" class="form-control" name="cc" value="${emailData.cc || ''}">
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Subject:</label>
                                <input type="text" class="form-control" name="subject" value="${emailData.subject || ''}" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Message:</label>
                                <textarea class="form-control" name="body" rows="10" required>${emailData.body || ''}</textarea>
                            </div>
                        </form>
                        <div class="email-preview mt-3">
                            <h6>Preview:</h6>
                            <div class="email-preview-content">
                                <strong>To:</strong> ${emailData.to || ''}<br>
                                <strong>Subject:</strong> ${emailData.subject || ''}<br><br>
                                <div style="white-space: pre-wrap;">${emailData.body || ''}</div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-outline-primary" onclick="openOutlookDraft(getEmailFormData())">Open in Outlook</button>
                        <button type="button" class="btn btn-primary" onclick="sendEmailFromForm()">Send Email</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal
    const existingModal = document.getElementById('emailDraftModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('emailDraftModal'));
    modal.show();
}

function getEmailFormData() {
    const form = document.getElementById('emailDraftForm');
    const formData = new FormData(form);
    return {
        to: formData.get('to'),
        cc: formData.get('cc'),
        subject: formData.get('subject'),
        body: formData.get('body')
    };
}

function sendEmailFromForm() {
    const emailData = getEmailFormData();
    sendEscalationEmail(currentSessionId, 'current-record-id', emailData);
}

// Chart Creation Functions
function createRiskDistributionChart(riskData) {
    const ctx = document.getElementById('mlInsightsChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [
                    riskData.Critical || 0,
                    riskData.High || 0,
                    riskData.Medium || 0,
                    riskData.Low || 0
                ],
                backgroundColor: [
                    '#dc3545',  // Critical - Red
                    '#fd7e14',  // High - Orange
                    '#ffc107',  // Medium - Yellow
                    '#198754'   // Low - Green
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Risk Distribution'
                }
            }
        }
    });
}

function createBAUChart(data) {
    const ctx = document.getElementById('bauAnalysisChart');
    if (!ctx || !data.frequency_analysis) return;
    
    const topSenders = data.frequency_analysis.top_senders || {};
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(topSenders).slice(0, 10),
            datasets: [{
                label: 'Communication Frequency',
                data: Object.values(topSenders).slice(0, 10),
                backgroundColor: '#0d6efd',
                borderColor: '#0d6efd',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Top Senders (BAU Analysis)'
                }
            }
        }
    });
}

function createAttachmentRiskChart(data) {
    const ctx = document.getElementById('attachmentRiskChart');
    if (!ctx || !data.risk_categories) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data.risk_categories),
            datasets: [{
                label: 'Attachment Count',
                data: Object.values(data.risk_categories),
                backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#0dcaf0', '#6c757d', '#e83e8c'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Attachment Risk Categories'
                }
            }
        }
    });
}

function createSenderBehaviorChart(data) {
    const ctx = document.getElementById('senderBehaviorChart');
    if (!ctx || !data.sender_profiles) return;
    
    const topSenders = Object.entries(data.sender_profiles).slice(0, 10);
    
    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Sender Risk vs Volume',
                data: topSenders.map(([sender, profile]) => ({
                    x: profile.total_emails,
                    y: profile.risk_score_avg,
                    sender: sender
                })),
                backgroundColor: '#0d6efd',
                borderColor: '#0d6efd'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Total Emails'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Average Risk Score'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Sender Behavior Analysis'
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].raw.sender;
                        }
                    }
                }
            }
        }
    });
}

function createTimePatternChart(data) {
    const ctx = document.getElementById('timePatternChart');
    if (!ctx || !data.hourly_distribution) return;
    
    const hours = Array.from({length: 24}, (_, i) => i);
    const hourlyData = hours.map(hour => data.hourly_distribution[hour] || 0);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours.map(h => `${h}:00`),
            datasets: [{
                label: 'Email Count',
                data: hourlyData,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Hourly Email Distribution'
                }
            }
        }
    });
}

function createWhitelistChart(data) {
    const ctx = document.getElementById('whitelistRecommendationsChart');
    if (!ctx || !data.whitelist_recommendations) return;
    
    const topRecommendations = data.whitelist_recommendations.slice(0, 10);
    
    new Chart(ctx, {
        type: 'horizontalBar',
        data: {
            labels: topRecommendations.map(r => r.domain),
            datasets: [{
                label: 'Communication Count',
                data: topRecommendations.map(r => r.communication_count),
                backgroundColor: '#198754'
            }, {
                label: 'Trust Score',
                data: topRecommendations.map(r => r.trust_score),
                backgroundColor: '#0dcaf0'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top Whitelist Recommendations'
                }
            }
        }
    });
}

// Utility Functions
function showLoading(message = 'Loading...') {
    if (loadingOverlay) {
        hideLoading();
    }
    
    loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'loading-overlay';
    loadingOverlay.innerHTML = `
        <div class="spinner-container">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div class="ms-3">${message}</div>
        </div>
    `;
    
    // Add overlay styles
    Object.assign(loadingOverlay.style, {
        position: 'fixed',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: '9999',
        color: 'white'
    });
    
    document.body.appendChild(loadingOverlay);
}

function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.remove();
        loadingOverlay = null;
    }
}

function showSuccess(message) {
    showAlert(message, 'success');
}

function showError(message) {
    showAlert(message, 'danger');
}

function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" style="top: 20px; right: 20px; z-index: 9999;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        if (alerts.length > 0) {
            alerts[alerts.length - 1].remove();
        }
    }, 5000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function applyFilters() {
    const filterForm = document.getElementById('filterForm');
    if (!filterForm) return;
    
    const formData = new FormData(filterForm);
    const params = new URLSearchParams();
    
    for (const [key, value] of formData.entries()) {
        if (value) {
            params.append(key, value);
        }
    }
    
    // Update URL and reload page with filters
    const currentUrl = new URL(window.location);
    currentUrl.search = params.toString();
    window.location.href = currentUrl.toString();
}

function checkProcessingStatus() {
    if (!currentSessionId) return;
    
    fetch(`/api/processing_status/${currentSessionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'completed') {
                location.reload(); // Refresh page when processing is complete
            }
        })
        .catch(error => {
            console.error('Error checking processing status:', error);
        });
}

function initializeCharts() {
    // Set default Chart.js configurations
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#495057';
    
    // Load charts based on current page
    setTimeout(() => {
        loadSessionContent();
    }, 500);
}

function initializeDataTables() {
    // Initialize DataTables for case management
    const caseTable = document.getElementById('casesTable');
    if (caseTable) {
        $(caseTable).DataTable({
            responsive: true,
            pageLength: 50,
            order: [[4, 'desc']], // Sort by risk score by default
            columnDefs: [
                { orderable: false, targets: [-1] } // Disable sorting on actions column
            ],
            language: {
                search: "Search cases:",
                lengthMenu: "Show _MENU_ cases per page",
                info: "Showing _START_ to _END_ of _TOTAL_ cases"
            }
        });
    }
}

// Expose functions globally for inline event handlers
window.showCaseDetails = showCaseDetails;
window.escalateCase = escalateCase;
window.updateCaseStatus = updateCaseStatus;
window.generateEscalationEmail = generateEscalationEmail;
window.openOutlookDraft = openOutlookDraft;
window.getEmailFormData = getEmailFormData;
window.sendEmailFromForm = sendEmailFromForm;
