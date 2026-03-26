document.addEventListener("DOMContentLoaded", () => {
    loadStats();
    setupDragAndDrop();
    setupFileInput();
});

/* Fetch and display document stats */
async function loadStats() {
    try {
        const res = await fetch("/api/documents/stats");
        const data = await res.json();
        document.getElementById("doc-count").textContent =
            `${data.total_documents} chunks`;
    } catch {
        document.getElementById("doc-count").textContent = "Unavailable";
    }
}

/* Drag-and-drop support */
function setupDragAndDrop() {
    const zone = document.getElementById("upload-zone");

    zone.addEventListener("dragover", (e) => {
        e.preventDefault();
        zone.classList.add("drag-over");
    });

    zone.addEventListener("dragleave", () => {
        zone.classList.remove("drag-over");
    });

    zone.addEventListener("drop", (e) => {
        e.preventDefault();
        zone.classList.remove("drag-over");
        const files = e.dataTransfer.files;
        if (files.length > 0) uploadFile(files[0]);
    });
}

/* File input change handler */
function setupFileInput() {
    document.getElementById("file-input").addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
            e.target.value = "";
        }
    });
}

/* Upload a PDF file to the server */
async function uploadFile(file) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
        showToast("Only PDF files are accepted", "danger");
        return;
    }

    const progressCard = document.getElementById("progress-card");
    const progressBar = document.getElementById("progress-bar");
    const progressStatus = document.getElementById("progress-status");
    const filename = document.getElementById("upload-filename");

    // Show progress UI
    progressCard.classList.remove("d-none");
    filename.textContent = file.name;
    progressBar.style.width = "0%";
    progressStatus.textContent = "Uploading...";

    // Simulate initial progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        if (progress < 70) {
            progress += Math.random() * 15;
            progressBar.style.width = `${Math.min(progress, 70)}%`;
        }
    }, 300);

    try {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("/api/documents/upload", {
            method: "POST",
            body: formData,
        });

        clearInterval(progressInterval);

        if (res.ok) {
            const data = await res.json();
            progressBar.style.width = "100%";
            progressStatus.textContent = `✓ ${data.message}`;
            progressBar.classList.remove("progress-bar-animated");
            showToast(
                `Added ${data.chunks_added} chunks from "${file.name}"`,
                "success",
            );
            addHistoryItem(file.name, data.chunks_added, true);
            loadStats();
        } else {
            const err = await res.json();
            progressBar.style.width = "100%";
            progressBar.classList.add("bg-danger");
            progressStatus.textContent = `✗ ${err.detail}`;
            showToast(err.detail, "danger");
            addHistoryItem(file.name, 0, false);
        }
    } catch (err) {
        clearInterval(progressInterval);
        progressBar.classList.add("bg-danger");
        progressStatus.textContent = "✗ Upload failed";
        showToast("Upload failed. Check server connection.", "danger");
        addHistoryItem(file.name, 0, false);
    }

    // Reset progress bar state after 3 seconds
    setTimeout(() => {
        progressBar.classList.remove("bg-danger");
        progressBar.classList.add("progress-bar-animated");
    }, 3000);
}

/* Add item to upload history */
function addHistoryItem(name, chunks, success) {
    const historyCard = document.getElementById("history-card");
    const historyList = document.getElementById("upload-history");
    historyCard.classList.remove("d-none");

    const icon = success ? "check-circle-fill" : "x-circle-fill";
    const info = success ? `${chunks} chunks added` : "Failed";

    const item = document.createElement("div");
    item.className = "history-item";
    item.innerHTML = `
        <i class="bi bi-${icon}"></i>
        <div class="flex-grow-1 text-truncate">
            <div class="fw-medium">${name}</div>
            <div class="text-muted small">${info}</div>
        </div>
    `;

    historyList.prepend(item);
}

/* Reset the knowledge base */
async function resetKnowledgeBase() {
    if (!confirm("This will permanently delete all documents from the knowledge base. Continue?")) {
        return;
    }

    try {
        const res = await fetch("/api/documents/reset", { method: "DELETE" });
        if (res.ok) {
            showToast("Knowledge base has been reset", "success");
            loadStats();
        } else {
            showToast("Failed to reset knowledge base", "danger");
        }
    } catch {
        showToast("Connection error", "danger");
    }
}

/* Show a Bootstrap toast notification */
function showToast(message, type = "info") {
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }

    const icons = {
        success: "check-circle-fill",
        danger: "exclamation-triangle-fill",
        info: "info-circle-fill",
    };

    const toast = document.createElement("div");
    toast.className = `toast show border-0 bg-dark text-white`;
    toast.setAttribute("role", "alert");
    toast.innerHTML = `
        <div class="toast-body d-flex align-items-center gap-2">
            <i class="bi bi-${icons[type] || icons.info} text-${type}"></i>
            <span>${message}</span>
        </div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add("fade");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
