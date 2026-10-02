-
const API_URL = "http://127.0.0.1:5000";

const lengthInput = document.getElementById("length");
const lengthValue = document.getElementById("lengthValue");
const useLower = document.getElementById("useLower");
const useUpper = document.getElementById("useUpper");
const useDigits = document.getElementById("useDigits");
const useSpecial = document.getElementById("useSpecial");
const excludeAmbiguous = document.getElementById("excludeAmbiguous");
const generateBtn = document.getElementById("generateBtn");
const generateResult = document.getElementById("generateResult");
const generatedPassword = document.getElementById("generatedPassword");
const copyBtn = document.getElementById("copyBtn");
const generateStrengthBar = document.getElementById("generateStrengthBar");
const generateStrengthLabel = document.getElementById("generateStrengthLabel");
const generateEntropy = document.getElementById("generateEntropy");
const generateError = document.getElementById("generateError");

const passwordInput = document.getElementById("passwordInput");
const toggleVisibilityBtn = document.getElementById("toggleVisibilityBtn");
const rateBtn = document.getElementById("rateBtn");
const rateResult = document.getElementById("rateResult");
const rateStrengthBar = document.getElementById("rateStrengthBar");
const rateStrengthLabel = document.getElementById("rateStrengthLabel");
const rateEntropy = document.getElementById("rateEntropy");
const feedbackList = document.getElementById("feedbackList");


lengthInput.addEventListener("input", () => {
  lengthValue.textContent = lengthInput.value;
});

function colorForScore(score) {
  if (score >= 90) return "var(--color-very-strong)";
  if (score >= 70) return "var(--color-strong)";
  if (score >= 50) return "var(--color-moderate)";
  return "var(--color-weak)";
}

function renderStrength(barEl, labelEl, entropyEl, result) {
  barEl.style.width = result.score + "%";
  barEl.style.backgroundColor = colorForScore(result.score);
  labelEl.textContent = `${result.label} (${result.score}%)`;
  entropyEl.textContent = `~${result.entropy_bits} bits`;
}

generateBtn.addEventListener("click", async () => {
  generateError.classList.add("hidden");

  const requestBody = {
    length: parseInt(lengthInput.value, 10),
    use_lower: useLower.checked,
    use_upper: useUpper.checked,
    use_digits: useDigits.checked,
    use_special: useSpecial.checked,
    exclude_ambiguous: excludeAmbiguous.checked,
  };

  try {
    const response = await fetch(`${API_URL}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    });

    const data = await response.json();

    if (!response.ok) {
      generateError.textContent = data.error || "Something went wrong.";
      generateError.classList.remove("hidden");
      generateResult.classList.add("hidden");
      return;
    }

    generatedPassword.textContent = data.password;
    renderStrength(generateStrengthBar, generateStrengthLabel, generateEntropy, data);
    generateResult.classList.remove("hidden");

  } catch (err) {
    generateError.textContent = "Could not reach the backend. Is api.py running?";
    generateError.classList.remove("hidden");
  }
});

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(generatedPassword.textContent).then(() => {
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy"), 1500);
  });
});
toggleVisibilityBtn.addEventListener("click", () => {
  const isHidden = passwordInput.type === "password";
  passwordInput.type = isHidden ? "text" : "password";
  toggleVisibilityBtn.textContent = isHidden ? "🙈" : "👁";
});

rateBtn.addEventListener("click", async () => {
  const password = passwordInput.value;

  try {
    const response = await fetch(`${API_URL}/api/rate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });

    const data = await response.json();

    renderStrength(rateStrengthBar, rateStrengthLabel, rateEntropy, data);

    feedbackList.innerHTML = ""; 
    data.feedback.forEach((line) => {
      const li = document.createElement("li");
      li.textContent = line;
      feedbackList.appendChild(li);
    });

    rateResult.classList.remove("hidden");

  } catch (err) {
    alert("Could not reach the backend. Is api.py running?");
  }
});
