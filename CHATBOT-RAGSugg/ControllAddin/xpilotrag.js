console.log("✅ Enhanced RAG ControlAddIn JS loaded");

document.body.innerHTML = `
  <div id="rag-draggable" class="rag-container resizable">
    <div class="rag-header" id="rag-header">
      <h2>📄 AI Document Analyzer</h2>
    </div>
    <div class="rag-body">
      <label for="prompt">📝 Prompt:</label>
      <textarea id="prompt" placeholder="E.g., Summarize this financial report..."></textarea>

      <label for="fileUpload">📎 Attach a PDF/Text file:</label>
      <input type="file" id="fileUpload" accept=".pdf,.txt">

      <button id="submit-btn">🚀 Run Analysis</button>

      <div id="response-container" class="rag-response">
        <h3>🤖 AI Response:</h3>
        <div id="spinner" class="spinner"></div>
        <pre id="responseText"></pre>
      </div>
      <div id="downloadContainer" style="margin-top:10px; display:none;">
        <a id="downloadLink" href="#" download target="_blank" rel="noopener noreferrer">
          📥 Download Response as DOCX
        </a>
      </div>
    </div>
  </div>
`;

(function enableDragAndResize() {
  const dragTarget = document.getElementById("rag-draggable");
  const dragHeader = document.getElementById("rag-header");
  let offsetX = 0, offsetY = 0, isDown = false;

  dragHeader.addEventListener("mousedown", (e) => {
    isDown = true;
    offsetX = e.clientX - dragTarget.offsetLeft;
    offsetY = e.clientY - dragTarget.offsetTop;
    dragHeader.style.cursor = "grabbing";
  });

  document.addEventListener("mousemove", (e) => {
    if (!isDown) return;
    dragTarget.style.left = e.clientX - offsetX + "px";
    dragTarget.style.top = e.clientY - offsetY + "px";
  });

  document.addEventListener("mouseup", () => {
    isDown = false;
    dragHeader.style.cursor = "grab";
  });

  // Resizable
  const resizeHandle = document.createElement("div");
  resizeHandle.className = "resize-handle";
  dragTarget.appendChild(resizeHandle);

  let isResizing = false;

  resizeHandle.addEventListener("mousedown", (e) => {
    e.preventDefault();
    isResizing = true;
  });

  document.addEventListener("mousemove", (e) => {
    if (!isResizing) return;
    dragTarget.style.width = e.clientX - dragTarget.offsetLeft + "px";
    dragTarget.style.height = e.clientY - dragTarget.offsetTop + "px";
  });

  document.addEventListener("mouseup", () => {
    isResizing = false;
  });
})();

const submitBtn = document.getElementById("submit-btn");
submitBtn.addEventListener("click", async () => {
  const prompt = document.getElementById("prompt").value.trim();
  const file = document.getElementById("fileUpload").files[0];
  const responseText = document.getElementById("responseText");
  const spinner = document.getElementById("spinner");
  const downloadContainer = document.getElementById("downloadContainer");
  const downloadLink = document.getElementById("downloadLink");

  if (!prompt && !file) {
    alert("❗ Please provide a prompt or upload a file.");
    return;
  }

  // Reset download link and hide container on new request
  downloadContainer.style.display = "none";
  downloadLink.href = "#";

  const formData = new FormData();
  formData.append("prompt", prompt);
  if (file) formData.append("file", file);

  responseText.innerText = "";
  spinner.style.display = "inline-block";

  try {
    const res = await fetch("http://localhost:8000/copilot/rag-process", {
      method: "POST",
      body: formData,
    });

    const result = await res.json();
    spinner.style.display = "none";

    if (result.success) {
      responseText.innerText = result.response_text || "✅ Done!";
      if (result.filename) {
        downloadLink.href = `http://localhost:8000/copilot/download-docx/${result.filename}`;
        downloadContainer.style.display = "block";
      }
    } else {
      responseText.innerText = `❌ Error: ${result.error}`;
      downloadContainer.style.display = "none";
    }
  } catch (err) {
    spinner.style.display = "none";
    responseText.innerText = `❌ Request failed: ${err.message}`;
    downloadContainer.style.display = "none";
  }
});
