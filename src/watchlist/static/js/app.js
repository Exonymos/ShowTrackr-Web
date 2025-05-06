// src/watchlist/static/js/app.js
let isFormDirty = false;
let tooltipTimeout;

function setFormDirty() {
  isFormDirty = true;
}

function resetFormDirtyFlag() {
  isFormDirty = false;
}

function checkUnsavedChangesAndCloseModal() {
  const modal = document.getElementById("add_item_modal");
  if (isFormDirty) {
    if (!confirm("You have unsaved changes. Are you sure you want to close?")) {
      return;
    }
  }
  resetFormDirtyFlag();
  if (modal && typeof modal.close === "function") {
    modal.close();
  }
}

// Reset filter
function resetFilters() {
  const filterForm = document.getElementById("filter-form");
  filterForm.reset(); // Reset the form fields to their initial values

  // Trigger an HTMX request to reload the watchlist with default filters
  htmx.ajax("GET", filterForm.getAttribute("hx-get"), {
    target: filterForm.getAttribute("hx-target"),
    swap: filterForm.getAttribute("hx-swap"),
    indicator: filterForm.getAttribute("hx-indicator"),
  });
}

// Poster Hover Logic
function showPosterTooltip(event) {
  clearTimeout(tooltipTimeout);
  const imgElement = event.target;
  const largePosterUrl = imgElement.dataset.largePoster;
  const tooltipElement = document.getElementById("poster-hover-tooltip");

  if (largePosterUrl && tooltipElement) {
    const largeImg = new Image();
    largeImg.onload = () => {
      tooltipElement.innerHTML = "";
      tooltipElement.appendChild(largeImg);

      // Calculate position
      const scrollX = window.scrollX || window.pageXOffset;
      const scrollY = window.scrollY || window.pageYOffset;
      let left = event.pageX + 15;
      let top = event.pageY + 15;

      // Basic boundary check
      const tooltipRect = tooltipElement.getBoundingClientRect();
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      const estWidth = Math.min(tooltipRect.width || 250, 250);
      const estHeight = tooltipRect.height || 375;

      if (left + estWidth > viewportWidth + scrollX) {
        left = event.pageX - estWidth - 15;
      }
      if (top + estHeight > viewportHeight + scrollY) {
        top = event.pageY - estHeight - 15;
      }
      if (left < scrollX) left = scrollX + 5;
      if (top < scrollY) top = scrollY + 5;

      tooltipElement.style.left = `${left}px`;
      tooltipElement.style.top = `${top}px`;
      tooltipElement.style.display = "block";
    };
    largeImg.onerror = () => {
      console.error("Failed to load large poster image for tooltip.");
      tooltipElement.style.display = "none";
    };
    largeImg.src = largePosterUrl;
    largeImg.alt = "Large Poster";
    largeImg.style.maxWidth = "250px";
    largeImg.style.maxHeight = "400px";
    largeImg.style.borderRadius = "0.25rem";
  }
}

function hidePosterTooltip() {
  // A short delay before hiding
  tooltipTimeout = setTimeout(() => {
    const tooltipElement = document.getElementById("poster-hover-tooltip");
    if (tooltipElement) {
      tooltipElement.style.display = "none";
      tooltipElement.innerHTML = "";
    }
  }, 100); // 100ms delay
}

// Event delegation for poster hover
document.addEventListener("mouseover", function (event) {
  if (event.target.matches(".poster-image")) {
    showPosterTooltip(event);
  }
  if (event.target.closest("#poster-hover-tooltip")) {
    clearTimeout(tooltipTimeout);
  }
});

document.addEventListener("mouseout", function (event) {
  if (event.target.matches(".poster-image")) {
    const tooltipElement = document.getElementById("poster-hover-tooltip");
    if (!tooltipElement || !tooltipElement.contains(event.relatedTarget)) {
      hidePosterTooltip();
    }
  }
  if (
    event.target.closest("#poster-hover-tooltip") &&
    !event.target.closest("#poster-hover-tooltip").contains(event.relatedTarget)
  ) {
    hidePosterTooltip();
  }
});

document.body.addEventListener("htmx:afterSwap", function (event) {
  const targetId = event.detail.target.id;

  // Modal Handling
  if (targetId === "modal-content") {
    resetFormDirtyFlag();
    const form = event.detail.target.querySelector("form");
    if (form) {
      form.querySelectorAll("input, textarea, select").forEach((input) => {
        input.addEventListener("input", setFormDirty);
        input.addEventListener("change", setFormDirty);
      });

      const itemIdInput = form.querySelector('input[name="item_id"]');
      const modalTitle = document.getElementById("modal-title");
      if (itemIdInput && itemIdInput.value && modalTitle) {
        modalTitle.textContent = "Edit Watchlist Item";
      } else if (modalTitle) {
        modalTitle.textContent = "Add New Watchlist Item";
      }
    }
  }

  // Modal Closing on Success
  const originatingElement = event.detail.requestConfig.elt;
  const modalElement = originatingElement
    ? originatingElement.closest(".modal")
    : null;

  if (
    modalElement &&
    event.detail.xhr.status === 200 &&
    event.detail.xhr.getResponseHeader("X-Close-Modal")
  ) {
    const modalId = modalElement.id;
    const modal = document.getElementById(modalId);
    resetFormDirtyFlag();
    if (modal && typeof modal.close === "function") {
      modal.close();
    }
  }
});

document.addEventListener("DOMContentLoaded", function () {
  // Keyboard shortcut for search
  function handleSearchShortcut(event) {
    if ((event.metaKey || event.ctrlKey) && event.key === "k") {
      event.preventDefault();
      const searchInput = document.getElementById("search-input");
      if (searchInput) {
        searchInput.focus();
      }
    }
  }

  document.addEventListener("keydown", handleSearchShortcut);
});

// Feedback Form Submission
const feedbackForm = document.getElementById("feedback-form");
const feedbackSubmitBtn = document.getElementById("feedback-submit-btn");
const feedbackStatusEl = document.getElementById("feedback-status");

if (feedbackForm && feedbackSubmitBtn) {
  const FEEDBACK_SCRIPT_URL =
    feedbackForm.dataset.feedbackUrl || document.body.dataset.feedbackUrl;
  const APP_VERSION =
    feedbackForm.querySelector('input[name="app_version"]')?.value || "unknown";

  feedbackForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!FEEDBACK_SCRIPT_URL) {
      showToast("Feedback submission URL is not configured.", "error");
      return;
    }

    const feedbackInput = document.getElementById("feedback-text");
    const submitButtonText =
      feedbackSubmitBtn.querySelector("span:not(.loading)");
    const submitButtonSpinner = feedbackSubmitBtn.querySelector(".loading");

    const feedbackText = feedbackInput.value.trim();
    if (!feedbackText) {
      showToast("Feedback cannot be empty.", "warning");
      feedbackInput.focus();
      return;
    }

    // Disable button and show spinner
    feedbackSubmitBtn.disabled = true;
    submitButtonText.classList.add("hidden");
    submitButtonSpinner.classList.remove("hidden");
    if (feedbackStatusEl) feedbackStatusEl.textContent = "Submitting...";

    // Create FormData
    const formData = new FormData(feedbackForm);
    const sendInfoCheckbox = document.getElementById("feedback-send-info");
    formData.set("sendInfo", sendInfoCheckbox.checked);

    if (sendInfoCheckbox.checked) {
      // Include userAgent if checked
      formData.set("userAgent", navigator.userAgent || "N/A");
    } else {
      // Ensure user agent isn't sent if unchecked
      formData.delete("userAgent");
    }

    try {
      const response = await fetch(FEEDBACK_SCRIPT_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        // Basic error handling for network issues
        throw new Error(`HTTP error ${response.status}`);
      }

      const resultText = await response.text();

      if (resultText.toLowerCase().includes("success")) {
        showToast("Feedback submitted successfully!", "success");
        feedbackForm.reset();
        if (feedbackStatusEl) feedbackStatusEl.textContent = "";
      } else {
        showToast(resultText || "Failed to submit feedback.", "error");
        if (feedbackStatusEl)
          feedbackStatusEl.textContent = resultText || "Submission failed.";
      }
    } catch (error) {
      console.error("Feedback submission error:", error);
      showToast(`Error submitting feedback: ${error.message}`, "error");
      if (feedbackStatusEl)
        feedbackStatusEl.textContent = "Error. Please try again.";
    } finally {
      // Re-enable button and hide spinner
      feedbackSubmitBtn.disabled = false;
      submitButtonText.classList.remove("hidden");
      submitButtonSpinner.classList.add("hidden");
    }
  });
}

// Toast Notifications
function showToast(message, type = "info") {
  const toastContainer =
    document.getElementById("toast-container") || createToastContainer();
  const toastId = "toast-" + Date.now();
  const alertClass =
    {
      success: "alert-success",
      error: "alert-error",
      warning: "alert-warning",
      info: "alert-info",
    }[type] || "alert-info";

  const toastHtml = `
                <div id="${toastId}" class="alert ${alertClass} shadow-lg text-sm py-2 px-4">
                    <span>${message}</span>
                </div>
            `;
  toastContainer.insertAdjacentHTML("beforeend", toastHtml);

  // Auto-remove toast after a few seconds
  setTimeout(() => {
    const toastElement = document.getElementById(toastId);
    if (toastElement) {
      toastElement.style.transition = "opacity 0.5s ease-out";
      toastElement.style.opacity = "0";
      setTimeout(() => toastElement.remove(), 500);
    }
  }, 4000); // 4 sec timeout
}

function createToastContainer() {
  const container = document.createElement("div");
  container.id = "toast-container";
  container.className = "toast toast-bottom toast-end z-[99]";
  document.body.appendChild(container);
  return container;
}

document.body.addEventListener("htmx:afterRequest", function (event) {
  const xhr = event.detail.xhr;
  const modal = document.getElementById("add_item_modal");

  if (xhr.status === 200 && xhr.getResponseHeader("X-Close-Modal")) {
    if (modal && typeof modal.close === "function") {
      modal.close();
    }
  }

  const message = xhr.getResponseHeader("X-HX-Alert");
  const messageType = xhr.getResponseHeader("X-HX-Alert-Type") || "info";
  if (message) {
    showToast(message, messageType);
  }
});

document.body.addEventListener("htmx:beforeSwap", function (evt) {
  if (
    evt.detail.xhr.status >= 400 &&
    evt.detail.target.id === "form-feedback"
  ) {
    if (evt.detail.serverResponse.includes("alert-error")) {
      showToast("Please correct the errors in the form.", "error");
    } else {
      showToast("An unexpected error occurred.", "error");
      evt.preventDefault();
    }
  }
});

// Handle Direct Page Input
function goToPage(event, inputElement) {
  if (event.type === "keydown" && event.key !== "Enter") {
    return;
  }
  event.preventDefault();

  const pageNum = inputElement.value;
  const targetUrl = inputElement.dataset.baseUrl;
  const currentParams = new URLSearchParams(inputElement.dataset.currentParams);

  if (
    pageNum &&
    parseInt(pageNum) > 0 &&
    parseInt(pageNum) <= parseInt(inputElement.max)
  ) {
    currentParams.set("page", pageNum);
    const finalUrl = `${targetUrl}?${currentParams.toString()}`;

    htmx.ajax("GET", finalUrl, {
      target: "#watchlist-content",
      swap: "innerHTML",
      indicator: "#htmx-indicator",
    });
  } else {
    showToast(
      `Please enter a valid page number (1-${inputElement.max}).`,
      "warning"
    );
  }
}
