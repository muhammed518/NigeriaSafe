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

  function requestAndSend() {
    if (!navigator.geolocation) {
      notify("Geolocation not supported by your browser.");
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
        notify("Unable to retrieve location: " + (err.message || err.code));
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
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
