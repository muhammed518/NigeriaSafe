// sos.js: attaches to .sos-button and posts geolocation to /api/sos-alert/
(function () {
  function notify(msg) {
    try {
      alert(msg);
    } catch (e) {
      console.log(msg);
    }
  }

  async function sendAlert(lat, lon, message) {
    try {
      const payload = { latitude: lat, longitude: lon };
      if (message) payload.message = message;

      const resp = await fetch("/api/sos-alert/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = await resp.json().catch(() => ({}));
      if (resp.ok) notify("SOS sent — help is being notified.");
      else notify("Failed to send SOS: " + (j.message || resp.statusText));
    } catch (e) {
      notify("Network error sending SOS.");
      console.error(e);
    }
  }

  async function sendAlertWithoutLocation(locationDescription, message) {
    try {
      const payload = { location_description: locationDescription };
      if (message) payload.message = message;

      const resp = await fetch("/api/sos-alert/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = await resp.json().catch(() => ({}));
      if (resp.ok) notify("SOS sent — help is being notified.");
      else notify("Failed to send SOS: " + (j.message || resp.statusText));
    } catch (e) {
      notify("Network error sending SOS.");
      console.error(e);
    }
  }

  function requestAndSend() {
    if (!navigator.geolocation) {
      console.log("Geolocation not supported");
      showManualLocationModal(null);
      return;
    }
    notify("Locating...");
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;

        // Use modal dialog to collect optional phone/message and confirm
        const modal = document.getElementById("sos-modal");
        const msgInput = document.getElementById("sos-message");
        const sendBtn = document.getElementById("sos-send");
        const cancelBtn = document.getElementById("sos-cancel");

        function openModal() {
          msgInput.value = "";
          modal.setAttribute("aria-hidden", "false");
          msgInput.focus();
        }
        function closeModal() {
          modal.setAttribute("aria-hidden", "true");
        }

        function cleanup() {
          sendBtn.removeEventListener("click", onSend);
          cancelBtn.removeEventListener("click", onCancel);
        }

        function onSend(ev) {
          ev.preventDefault();
          const message =
            msgInput.value && msgInput.value.trim()
              ? msgInput.value.trim()
              : null;
          closeModal();
          cleanup();
          sendAlert(lat, lon, message);
        }

        function onCancel(ev) {
          ev.preventDefault();
          closeModal();
          cleanup();
          notify("SOS cancelled.");
        }

        sendBtn.addEventListener("click", onSend);
        cancelBtn.addEventListener("click", onCancel);
        openModal();
      },
      function (err) {
        // Geolocation failed or permission denied
        console.log("Geolocation error code:", err.code);
        console.log("Geolocation error message:", err.message);
        console.log("About to show manual location modal");
        showManualLocationModal(err);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  function showManualLocationModal(geoError) {
    console.log("showManualLocationModal called");
    const modal = document.getElementById("sos-location-modal");
    console.log("Modal element found:", !!modal);
    
    if (!modal) {
      console.error("sos-location-modal element not found in DOM");
      notify("Location input modal not found. Please refresh the page.");
      return;
    }

    const backdrop = modal.querySelector(".sos-modal-backdrop");
    const locationInput = document.getElementById("sos-location-input");
    const msgInput = document.getElementById("sos-location-message");
    const sendBtn = document.getElementById("sos-location-send");
    const cancelBtn = document.getElementById("sos-location-cancel");

    console.log("Form elements found:", {
      backdrop: !!backdrop,
      locationInput: !!locationInput,
      msgInput: !!msgInput,
      sendBtn: !!sendBtn,
      cancelBtn: !!cancelBtn
    });

    if (!locationInput || !msgInput || !sendBtn || !cancelBtn) {
      console.error("One or more form elements not found");
      notify("Form elements missing. Please refresh the page.");
      return;
    }

    function openModal() {
      console.log("Opening manual location modal");
      locationInput.value = "";
      msgInput.value = "";
      modal.setAttribute("aria-hidden", "false");
      console.log("Modal aria-hidden set to false");
      locationInput.focus();
    }

    function closeModal() {
      modal.setAttribute("aria-hidden", "true");
    }

    function cleanup() {
      sendBtn.removeEventListener("click", onSend);
      cancelBtn.removeEventListener("click", onCancel);
      if (backdrop) backdrop.removeEventListener("click", onBackdropClick);
    }

    function onSend(ev) {
      ev.preventDefault();
      const location = locationInput.value && locationInput.value.trim() 
        ? locationInput.value.trim() 
        : null;
      const message = msgInput.value && msgInput.value.trim()
        ? msgInput.value.trim()
        : null;

      if (!location) {
        notify("Please enter your location or nearby landmarks.");
        return;
      }

      closeModal();
      cleanup();
      sendAlertWithoutLocation(location, message);
    }

    function onCancel(ev) {
      ev.preventDefault();
      closeModal();
      cleanup();
      notify("SOS cancelled.");
    }

    function onBackdropClick(ev) {
      if (ev.target === backdrop) {
        onCancel(ev);
      }
    }

    sendBtn.addEventListener("click", onSend);
    cancelBtn.addEventListener("click", onCancel);
    if (backdrop) backdrop.addEventListener("click", onBackdropClick);
    openModal();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document
      .querySelectorAll(".sos-button, .phone-sos-btn")
      .forEach(function (el) {
        el.addEventListener("click", function (ev) {
          ev.preventDefault();
          requestAndSend();
        });
      });
  });
})();
