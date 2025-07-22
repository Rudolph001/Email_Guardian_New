/**
 * Mac-specific upload fixes for Email Guardian
 * This script provides fallback functionality for Mac browsers
 */

// Mac-specific file upload enhancements
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mac upload fix loaded');
    
    // Enhanced file validation for Mac
    function validateFile(file) {
        if (!file) {
            alert('Please select a file');
            return false;
        }
        
        if (!file.name.toLowerCase().endsWith('.csv')) {
            alert('Please select a CSV file');
            return false;
        }
        
        if (file.size > 500 * 1024 * 1024) { // 500MB
            alert('File size must be less than 500MB');
            return false;
        }
        
        return true;
    }
    
    // Simplified file display function
    function displaySelectedFileMac(file) {
        const fileInfo = document.getElementById('fileInfo');
        const uploadBtn = document.getElementById('uploadBtn');
        
        if (fileInfo && uploadBtn) {
            const sizeText = formatFileSize(file.size);
            fileInfo.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-file-csv"></i>
                    <strong>Selected:</strong> ${file.name} (${sizeText})
                </div>
            `;
            uploadBtn.disabled = false;
        }
    }
    
    // Simple file size formatter
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Enhanced form submission for Mac
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!validateFile(file)) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
            }
            
            console.log('Form submitted with file:', file.name);
            return true;
        });
    }
    
    // Enhanced file input handling for Mac
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && validateFile(file)) {
                displaySelectedFileMac(file);
                console.log('File selected:', file.name, file.size);
            }
        });
    }
    
    // Enhanced drag and drop for Mac
    const fileUploadArea = document.getElementById('fileUploadArea');
    if (fileUploadArea) {
        // Prevent default browser behavior
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Highlight drop area
        ['dragenter', 'dragover'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            fileUploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight(e) {
            fileUploadArea.classList.add('dragover');
        }
        
        function unhighlight(e) {
            fileUploadArea.classList.remove('dragover');
        }
        
        // Handle dropped files
        fileUploadArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                const file = files[0];
                if (validateFile(file)) {
                    fileInput.files = files;
                    displaySelectedFileMac(file);
                    console.log('File dropped:', file.name, file.size);
                }
            }
        }
        
        // Click to browse
        fileUploadArea.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    // Error handling for unknown upload URL issues
    window.addEventListener('error', function(e) {
        if (e.message && e.message.includes('unknownUploadURL')) {
            console.warn('Upload URL error detected, using fallback');
            // Force form submission without JavaScript validation
            const form = document.getElementById('uploadForm');
            if (form) {
                form.setAttribute('action', '/upload');
                form.submit();
            }
        }
    });
});