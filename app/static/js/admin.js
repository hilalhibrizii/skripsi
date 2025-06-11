// static/js/admin.js

// Konfigurasi Marked.js
marked.setOptions({
    breaks: true,
    gfm: true,
    sanitize: false,
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value;
            } catch (err) {
                console.warn(`Highlight.js error for language ${lang}:`, err);
            }
        }
        return hljs.highlightAuto(code).value;
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const intentsTableBody = document.querySelector('#intentsTable tbody');
    const editModal = document.getElementById('editModal');
    const editIntentForm = document.getElementById('editIntentForm');
    const closeModal = document.querySelector('.close');
    const cancelBtn = document.querySelector('.cancel-btn');
    const editResponses = document.getElementById('editResponses');
    const markdownPreview = document.getElementById('markdownPreview');
    const previewToggle = document.getElementById('previewToggle');
    
    let currentEditingIntent = null;
    let isPreviewMode = false; // Status mode pratinjau (false = Raw/Edit, true = Preview)

    // ... (Fungsi fetchIntents, truncateText, stripHtml, stripMarkdown tetap sama) ...
    async function fetchIntents() {
        try {
            const response = await fetch('/intents');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const intents = await response.json();
            renderIntents(intents);
        } catch (error) {
            console.error('Error fetching intents:', error);
            alert('Gagal memuat data. Silakan coba lagi.');
        }
    }

    function truncateText(text, maxLength) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + '...';
    }

    function stripHtml(html) {
        let doc = new DOMParser().parseFromString(html, 'text/html');
        return doc.body.textContent || "";
    }

    function stripMarkdown(markdown) {
        return markdown
            .replace(/#{1,6}\s+/g, '') // Headers
            .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
            .replace(/\*(.*?)\*/g, '$1') // Italic
            .replace(/`(.*?)`/g, '$1') // Inline code
            .replace(/```[\s\S]*?```/g, '[Code Block]') // Code blocks
            .replace(/^\s*[-*+]\s+/gm, '• ') // List items
            .replace(/^\s*\d+\.\s+/gm, '• ') // Numbered lists
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links
            .replace(/!\[([^\]]*)\]\([^)]+\)/g, '[Image: $1]') // Images
            .trim();
    }

    function renderIntents(intents) {
        intentsTableBody.innerHTML = '';
        intents.forEach(intent => {
            const row = document.createElement('tr');

            const tagCell = document.createElement('td');
            tagCell.textContent = intent.tag;
            row.appendChild(tagCell);

            const patternsCell = document.createElement('td');
            const displayPattern = intent.patterns.length > 0 ? intent.patterns[0] : 'Tidak ada pattern';
            patternsCell.textContent = truncateText(displayPattern, 50);
            row.appendChild(patternsCell);

            const responsesCell = document.createElement('td');
            let fullResponsesText = intent.responses.length > 0 ? intent.responses.join('\n') : 'Tidak ada respon';
            
            const responseContainer = document.createElement('div');
            
            const toggleBtn = document.createElement('button');
            toggleBtn.textContent = 'Preview'; // Teks tombol tetap 'Preview'
            toggleBtn.className = 'view-toggle';
            
            const contentDiv = document.createElement('div');
            // Default: tampilkan sebagai raw text, jadi gunakan stripMarkdown
            contentDiv.className = 'response-content raw-content';
            contentDiv.textContent = truncateText(stripMarkdown(fullResponsesText), 100);

            // Tambahkan event listener untuk toggle
            toggleBtn.onclick = function(e) {
                e.stopPropagation();
                const isRaw = toggleBtn.textContent === 'Preview'; // Jika tombolnya 'Preview', berarti yang tampil sekarang adalah Raw

                if (isRaw) {
                    // Jika sekarang menampilkan raw text, ubah ke tampilan pratinjau Markdown
                    contentDiv.innerHTML = marked.parse(fullResponsesText);
                    contentDiv.className = 'response-content markdown-content';
                    toggleBtn.textContent = 'Raw'; // Ganti teks tombol menjadi 'Raw'
                } else {
                    // Jika sekarang menampilkan pratinjau Markdown, ubah ke tampilan raw text
                    contentDiv.textContent = truncateText(stripMarkdown(fullResponsesText), 100);
                    contentDiv.className = 'response-content raw-content';
                    toggleBtn.textContent = 'Preview'; // Ganti teks tombol menjadi 'Preview'
                }
            };
            
            responseContainer.appendChild(toggleBtn);
            responseContainer.appendChild(contentDiv);
            responsesCell.appendChild(responseContainer);
            row.appendChild(responsesCell);

            const actionsCell = document.createElement('td');
            const editButton = document.createElement('button');
            editButton.textContent = 'Edit Respon';
            editButton.classList.add('edit-btn');
            editButton.addEventListener('click', () => openEditModal(intent));

            actionsCell.appendChild(editButton);
            row.appendChild(actionsCell);

            intentsTableBody.appendChild(row);
        });
    }

    function openEditModal(intent) {
        currentEditingIntent = intent;
        
        document.getElementById('editTag').value = intent.tag;
        document.getElementById('displayTag').textContent = intent.tag;
        
        document.getElementById('editResponses').value = intent.responses.join('\n');
        
        // Pastikan saat modal dibuka, mode default adalah "Edit" (raw textarea)
        isPreviewMode = false; // Set ke false secara default
        editResponses.style.display = 'block'; // Tampilkan textarea
        markdownPreview.style.display = 'none'; // Sembunyikan preview
        previewToggle.textContent = 'Preview'; // Pastikan tombol menampilkan 'Preview'
        
        editModal.style.display = 'block';
    }

    function closeEditModal() {
        editModal.style.display = 'none';
        currentEditingIntent = null; 
    }

    closeModal.onclick = closeEditModal;
    cancelBtn.onclick = closeEditModal;

    window.onclick = function (event) {
        if (event.target === editModal) {
            closeEditModal();
        }
    };

    // Toggle preview mode di dalam modal
    previewToggle.addEventListener('click', function() {
        isPreviewMode = !isPreviewMode;
        if (isPreviewMode) {
            editResponses.style.display = 'none';
            markdownPreview.style.display = 'block';
            markdownPreview.innerHTML = marked.parse(editResponses.value);
            previewToggle.textContent = 'Edit';
        } else {
            editResponses.style.display = 'block';
            markdownPreview.style.display = 'none';
            previewToggle.textContent = 'Preview';
        }
    });

    editResponses.addEventListener('input', function() {
        if (isPreviewMode) {
            markdownPreview.innerHTML = marked.parse(this.value);
        }
    });

    editIntentForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const tag = document.getElementById('editTag').value;
        const rawResponses = document.getElementById('editResponses').value;

        const responses = rawResponses.split('\n');

        const updateData = {
            responses: responses,
            patterns: currentEditingIntent ? currentEditingIntent.patterns : []
        };

        try {
            const response = await fetch(`/intents/${tag}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData) 
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Update gagal');
            }

            fetchIntents();
            closeEditModal();
            alert('Respon berhasil diperbarui!');
        } catch (error) {
            console.error('Error updating intent:', error);
            alert('Gagal memperbarui respon. Silakan coba lagi. Detail: ' + error.message);
        }
    });

    fetchIntents();
});