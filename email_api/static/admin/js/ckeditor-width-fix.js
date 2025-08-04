// CKEditor 5 Width Fix for Django Admin
document.addEventListener('DOMContentLoaded', function() {
    // Function to fix CKEditor width
    function fixCKEditorWidth() {
        // Wait for CKEditor to initialize
        setTimeout(function() {
            const editors = document.querySelectorAll('.ck-editor');
            editors.forEach(function(editor) {
                // Force max-width constraint
                editor.style.maxWidth = '100%';
                editor.style.width = '100%';
                editor.style.boxSizing = 'border-box';
                
                // Get the parent container
                const parent = editor.closest('.form-row');
                if (parent) {
                    parent.style.overflowX = 'auto';
                }
                
                // Fix the editable area
                const editable = editor.querySelector('.ck-editor__editable');
                if (editable) {
                    editable.style.maxWidth = '100%';
                    editable.style.boxSizing = 'border-box';
                    editable.style.overflowX = 'auto';
                    editable.style.wordWrap = 'break-word';
                }
                
                // Fix the toolbar
                const toolbar = editor.querySelector('.ck-toolbar');
                if (toolbar) {
                    toolbar.style.maxWidth = '100%';
                    toolbar.style.flexWrap = 'wrap';
                    toolbar.style.overflowX = 'auto';
                }
            });
        }, 500);
    }
    
    // Run the fix initially
    fixCKEditorWidth();
    
    // Also run when window is resized
    window.addEventListener('resize', fixCKEditorWidth);
    
    // Monitor for new CKEditor instances (in case of dynamic loading)
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                Array.from(mutation.addedNodes).forEach(function(node) {
                    if (node.nodeType === 1 && 
                        (node.classList.contains('ck-editor') || 
                         node.querySelector('.ck-editor'))) {
                        fixCKEditorWidth();
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
