const form = document.querySelector("#design-form");
const templateSelect = document.querySelector("#template");
const statusEl = document.querySelector("#status");
const summaryEl = document.querySelector("#summary");
const gcodeEl = document.querySelector("#gcode");
const downloadButton = document.querySelector("#download");
let latestGcode = "";

async function loadTemplates() {
  const response = await fetch("/api/templates");
  const templates = await response.json();
  templateSelect.innerHTML = templates
    .map((template) => `<option value="${template.id}">${template.label} — ${template.description}</option>`)
    .join("");
}

function formPayload() {
  const data = new FormData(form);
  return Object.fromEntries([...data.entries()].map(([key, value]) => {
    if (["width", "depth", "height", "spacing"].includes(key)) return [key, Number.parseFloat(value)];
    if (["feedrate", "travel_feedrate"].includes(key)) return [key, Number.parseInt(value, 10)];
    return [key, value];
  }));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusEl.textContent = "Generating…";
  downloadButton.disabled = true;

  const response = await fetch("/api/gcode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formPayload()),
  });
  const payload = await response.json();

  if (!response.ok) {
    statusEl.textContent = payload.error || "Unable to generate G-code.";
    return;
  }

  latestGcode = payload.gcode;
  gcodeEl.textContent = latestGcode;
  const bounds = payload.estimated_bounds;
  summaryEl.textContent = `${payload.point_count} points · X ${bounds.min_x.toFixed(1)}–${bounds.max_x.toFixed(1)} mm · Y ${bounds.min_y.toFixed(1)}–${bounds.max_y.toFixed(1)} mm`;
  statusEl.textContent = "Ready to copy or download.";
  downloadButton.disabled = false;
});

downloadButton.addEventListener("click", () => {
  const blob = new Blob([latestGcode], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "easygcode-output.gcode";
  link.click();
  URL.revokeObjectURL(url);
});

loadTemplates().catch(() => {
  statusEl.textContent = "Could not load templates. Is the local server running?";
});
