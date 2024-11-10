class CodeAnalyzer {
  constructor() {
    this.dropZone = document.getElementById("dropZone");
    this.fileInput = document.getElementById("fileInput");
    this.fileList = document.getElementById("fileList");
    this.progressBar = document.getElementById("uploadProgress");
    this.analysisResults = document.getElementById("analysisResults");
    this.analysisContent = document.getElementById("analysisContent");

    this.initializeEventListeners();
    this.initializeMDC();
  }

  initializeEventListeners() {
    // Drag and drop handlers
    this.dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      this.dropZone.classList.add("drag-over");
    });

    this.dropZone.addEventListener("dragleave", () => {
      this.dropZone.classList.remove("drag-over");
    });

    this.dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      this.dropZone.classList.remove("drag-over");
      this.handleFiles(e.dataTransfer.files);
    });

    // File input handler
    this.fileInput.addEventListener("change", (e) => {
      this.handleFiles(e.target.files);
    });
  }

  async handleFiles(files) {
    const formData = new FormData();
    let fileCount = 0;

    for (const file of files) {
      // TODO: For quickness/simplicity just handling .py now,
      // but would like to account for more types down the line
      if (file.name.endsWith(".py")) {
        formData.append("files", file);
        fileCount++;
      }
    }

    if (fileCount === 0) {
      this.showError("Please select Python (.py) files");
      return;
    }

    this.showProgress();

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      const results = await response.json();
      this.displayResults(results);
    } catch (error) {
      this.showError(error.message);
    } finally {
      this.hideProgress();
    }
  }

  displayResults(results) {
    this.analysisResults.style.display = "block";
    this.updateAnalysisContent(results);
  }

  updateAnalysisContent(results) {
    // Create tabs for different result types
    const content = {
      functions: this.createFunctionsView(results.functions),
      classes: this.createClassesView(results.classes),
      relationships: this.createRelationshipsView(results.relationships),
    };

    this.analysisContent.innerHTML = content.functions; // Default to functions view
  }

  createFunctionsView(functions) {
    return `
          <div class="mdc-data-table">
              <table class="mdc-data-table__table">
                  <thead>
                      <tr class="mdc-data-table__header-row">
                          <th class="mdc-data-table__header-cell">File</th>
                          <th class="mdc-data-table__header-cell">Function Name</th>
                          <th class="mdc-data-table__header-cell">Location</th>
                      </tr>
                  </thead>
                  <tbody class="mdc-data-table__content">
                      ${functions
                        .map(
                          (fn) => `
                          <tr class="mdc-data-table__row">
                              <td class="mdc-data-table__cell">${fn.file}</td>
                              <td class="mdc-data-table__cell">${fn.name}</td>
                              <td class="mdc-data-table__cell">Line ${fn.location}</td>
                          </tr>
                      `
                        )
                        .join("")}
                  </tbody>
              </table>
          </div>
      `;
  }

  // Similar methods for classes and relationships views...

  showProgress() {
    this.progressBar.style.display = "block";
  }

  hideProgress() {
    this.progressBar.style.display = "none";
  }

  showError(message) {
    const snackbar = new mdc.snackbar.MDCSnackbar(
      document.querySelector(".mdc-snackbar")
    );
    snackbar.labelText = message;
    snackbar.open();
    console.error("main.js error:", message);
  }
}

// Initialize when the document is loaded
document.addEventListener("DOMContentLoaded", () => {
  new CodeAnalyzer();
});
