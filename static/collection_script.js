// Utility function for fetching API data
async function fetchApi(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(endpoint, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.message || 'Something went wrong');
        }

        return result;
    } catch (error) {
        console.error(`Error in ${method} ${endpoint}:`, error);
        throw error;
    }
}

// Load and display indexed files in the sidebar
async function loadIndexedFiles() {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = ""; // Clear existing entries

    try {
        const { data: files } = await fetchApi('/listcollection');

        if (files?.length) {
            files.forEach((file) => {
                const listItem = document.createElement('li');
                listItem.className = 'file-item';

                const fileNameSpan = document.createElement('span');
                fileNameSpan.textContent = file;
                fileNameSpan.className = 'file-name';

                const deleteIcon = document.createElement('span');
                deleteIcon.className = 'fa fa-trash delete-icon';
                deleteIcon.title = "Delete file";
                deleteIcon.onclick = () => deleteIndexedFile(file);

                listItem.append(fileNameSpan, deleteIcon);
                fileList.appendChild(listItem);
            });
        } else {
            fileList.innerHTML = `<li class="no-files-message">No indexed files found.</li>`;
        }
    } catch (error) {
        fileList.innerHTML = `<li class="no-files-message">Error loading files.</li>`;
    }
}

// Delete an indexed file
async function deleteIndexedFile(filename) {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) return;

    try {
        await fetchApi('/deletecollection', 'POST', { filename });
        alert(`File "${filename}" deleted successfully.`);
        await loadIndexedFiles();
    } catch (error) {
        alert(`Error deleting file "${filename}": ${error.message}`);
    }
}

// Upload a PDF file
async function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const messageDiv = document.getElementById('message');
    const file = fileInput.files[0];

    if (!file) {
        messageDiv.textContent = "Please select a file to upload.";
        return;
    }

    spinner.style.display = 'block';
    messageDiv.textContent = ''; // Clear the message div

    const formData = new FormData();
    formData.append('pdf', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        if (response.ok) {
            messageDiv.textContent = result.message;
            await loadIndexedFiles();
        } else {
            messageDiv.textContent = `Error: ${result.message}`;
        }
    } catch (error) {
        messageDiv.textContent = "Error uploading file.";
        console.error(error);
    }finally {
        // Hide the spinner after uploading
        spinner.style.display = 'none';
    }
}

// Execute a search and display results
async function searchFiles() {
    const searchInput = document.getElementById('search-input');
    const searchResultsDiv = document.getElementById('search-results');
    const query = searchInput.value.trim();

    searchResultsDiv.innerHTML = ""; // Clear previous results
    spinner2.style.display = 'block';
  

    if (!query) {
        searchResultsDiv.textContent = "Please enter search keywords.";
        return;
    }

    try {
        const { data: results } = await fetchApi('/search', 'POST', { query });
        searchResultsDiv.innerHTML = "<h3>Search Results:</h3>";

        if (results?.length) {
            results.forEach(({ filename, page, text }) => {
                const resultDiv = document.createElement('div');
                resultDiv.className = 'result-item';

                resultDiv.innerHTML = `
                    <h4>File: ${filename} (Page ${page})</h4>
                    <p>Text: ${text}</p>
                `;

                searchResultsDiv.appendChild(resultDiv);
            });
        } else {
            searchResultsDiv.innerHTML += "<p>No results found.</p>";
        }
    } catch (error) {
        searchResultsDiv.textContent = "Error searching files.";
    }finally {
        // Hide the spinner after uploading
        spinner2.style.display = 'none';
    }
}

// Bind event listeners
document.getElementById('upload-button').addEventListener('click', uploadFile);
document.getElementById('search-button').addEventListener('click', searchFiles);

// Load indexed files on page load
window.onload = loadIndexedFiles;