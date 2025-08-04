/**
 * CKEditor Placeholder Insertion Helper
 * 
 * This script provides functionality to insert template placeholders
 * into CKEditor 5 instances in Django admin forms.
 */

window.CKEditorPlaceholderHelper = (function() {
    'use strict';

    let editorInstance = null;
    let isDebugMode = false;

    function log(message) {
        if (isDebugMode) {
            console.log('[CKEditor Placeholder Helper]', message);
        }
    }

    function findEditorInstance() {
        // Method 1: Check if we have a cached instance
        if (editorInstance && editorInstance.model) {
            return editorInstance;
        }

        // Method 2: Look for ClassicEditor instances
        if (window.ClassicEditor && window.ClassicEditor.instances) {
            for (let instance of window.ClassicEditor.instances) {
                if (instance.model && instance.editing) {
                    editorInstance = instance;
                    log('Found editor via ClassicEditor.instances');
                    return instance;
                }
            }
        }

        // Method 3: Look for editor attached to DOM elements
        const bodyField = document.querySelector('[name="body"]');
        if (bodyField && bodyField.ckeditorInstance) {
            editorInstance = bodyField.ckeditorInstance;
            log('Found editor via body field');
            return editorInstance;
        }

        // Method 4: Look for editor in the editable container
        const editableContainer = document.querySelector('.ck-editor__editable');
        if (editableContainer) {
            // Try to find the editor instance from the container
            const editor = editableContainer.closest('.ck-editor');
            if (editor && editor.ckeditorInstance) {
                editorInstance = editor.ckeditorInstance;
                log('Found editor via editable container');
                return editorInstance;
            }
        }

        log('No editor instance found');
        return null;
    }

    function insertTextAtCursor(text) {
        const editor = findEditorInstance();
        
        if (!editor) {
            log('No editor found for text insertion');
            return false;
        }

        try {
            editor.model.change(writer => {
                const selection = editor.model.document.selection;
                const position = selection.getFirstPosition();
                writer.insertText(text, position);
            });
            
            // Focus the editor after insertion
            editor.editing.view.focus();
            log(`Successfully inserted: ${text}`);
            return true;
        } catch (error) {
            log(`Error inserting text: ${error.message}`);
            return false;
        }
    }

    function insertAtTextareaFallback(text) {
        const bodyField = document.querySelector('[name="body"]');
        
        if (!bodyField) {
            return false;
        }

        try {
            if (bodyField.selectionStart !== undefined) {
                const start = bodyField.selectionStart;
                const end = bodyField.selectionEnd;
                const value = bodyField.value;
                
                bodyField.value = value.substring(0, start) + text + value.substring(end);
                bodyField.selectionStart = bodyField.selectionEnd = start + text.length;
                bodyField.focus();
                
                log(`Fallback insertion successful: ${text}`);
                return true;
            }
        } catch (error) {
            log(`Fallback insertion failed: ${error.message}`);
        }
        
        return false;
    }

    function initializeEditorDetection() {
        let attempts = 0;
        const maxAttempts = 30; // 6 seconds with 200ms intervals

        function detectEditor() {
            attempts++;
            
            if (findEditorInstance()) {
                log('Editor detection successful');
                return;
            }

            if (attempts < maxAttempts) {
                setTimeout(detectEditor, 200);
            } else {
                log('Editor detection timed out');
            }
        }

        detectEditor();
    }

    // Public API
    return {
        insertPlaceholder: function(placeholder) {
            log(`Attempting to insert placeholder: ${placeholder}`);
            
            // Try CKEditor insertion first
            if (insertTextAtCursor(placeholder)) {
                return true;
            }
            
            // Fallback to textarea
            if (insertAtTextareaFallback(placeholder)) {
                return true;
            }
            
            // Show user-friendly error
            alert('Please click inside the email body editor first, then try inserting the placeholder again.');
            return false;
        },

        setDebugMode: function(enabled) {
            isDebugMode = enabled;
        },

        getEditorInstance: function() {
            return findEditorInstance();
        },

        initialize: function() {
            log('Initializing CKEditor detection');
            initializeEditorDetection();
            
            // Listen for potential CKEditor ready events
            if (typeof window.addEventListener === 'function') {
                window.addEventListener('ckeditor5:ready', function(event) {
                    log('CKEditor ready event detected');
                    editorInstance = event.detail?.editor;
                });
            }
        }
    };
})();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.CKEditorPlaceholderHelper.initialize();
});

// Expose global function for backward compatibility
window.insertPlaceholder = function(placeholder) {
    const success = window.CKEditorPlaceholderHelper.insertPlaceholder(placeholder);
    
    if (success) {
        // Show visual feedback
        const button = event?.target;
        if (button) {
            const originalText = button.textContent;
            const originalBg = button.style.backgroundColor;
            
            button.textContent = '✅ Inserted!';
            button.style.backgroundColor = '#28a745';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.backgroundColor = originalBg || '#007cba';
            }, 1500);
        }
    }
    
    return success;
};
