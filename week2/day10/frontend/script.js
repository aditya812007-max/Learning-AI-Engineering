// Backend API configuration
const DEFAULT_API_BASE = "http://localhost:8000";
let apiBase = localStorage.getItem("cafe_api_base") || DEFAULT_API_BASE;

// Web Audio API Retro Sound Synthesizer
class SoundEffects {
  constructor() {
    this.audioCtx = null;
    this.soundEnabled = true;
  }

  init() {
    if (!this.audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) this.audioCtx = new AudioContext();
    }
  }

  playBlip() {
    if (!this.soundEnabled) return;
    this.init();
    if (!this.audioCtx) return;
    try {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(440, this.audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(880, this.audioCtx.currentTime + 0.05);
      gain.gain.setValueAtTime(0.06, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.05);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.05);
    } catch (e) {}
  }

  playBell() {
    if (!this.soundEnabled) return;
    this.init();
    if (!this.audioCtx) return;
    try {
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(1200, this.audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(600, this.audioCtx.currentTime + 0.4);
      gain.gain.setValueAtTime(0.2, this.audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.audioCtx.currentTime + 0.4);
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start();
      osc.stop(this.audioCtx.currentTime + 0.4);
    } catch (e) {}
  }
}

const sfx = new SoundEffects();

// DOM Elements
const chatStream = document.getElementById("chatStream");
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const baristaBubble = document.getElementById("baristaBubble");
const bellRing = document.getElementById("bellRing");
const soundToggle = document.getElementById("soundToggle");
const clearChat = document.getElementById("clearChat");
const configEndpointBtn = document.getElementById("configEndpointBtn");
const endpointLabel = document.getElementById("endpointLabel");
const steamContainer = document.getElementById("steamContainer");

// Ambient Steam particles
function createSteam() {
  if (!steamContainer) return;
  for (let i = 0; i < 6; i++) {
    const steam = document.createElement("div");
    steam.className = "steam-particle";
    steam.style.left = `${20 + Math.random() * 60}%`;
    steam.style.animationDelay = `${Math.random() * 5}s`;
    steam.style.animationDuration = `${5 + Math.random() * 4}s`;
    steamContainer.appendChild(steam);
  }
}
createSteam();

// Update API Endpoint label
function updateEndpointLabel() {
  if (endpointLabel) endpointLabel.textContent = `${apiBase}/chat`;
}
updateEndpointLabel();

// Config button handler
if (configEndpointBtn) {
  configEndpointBtn.addEventListener("click", () => {
    const next = prompt("Enter your FastAPI Backend URL:", apiBase);
    if (next && next.trim()) {
      apiBase = next.trim().replace(/\/+$/, "");
      localStorage.setItem("cafe_api_base", apiBase);
      updateEndpointLabel();
      displayNpcMessage(`Backend URL updated to: ${apiBase}/chat`);
    }
  });
}

// Sound toggle
if (soundToggle) {
  soundToggle.addEventListener("click", () => {
    sfx.soundEnabled = !sfx.soundEnabled;
    soundToggle.textContent = sfx.soundEnabled ? "🔊 SFX" : "🔇 SFX";
    if (sfx.soundEnabled) sfx.playBlip();
  });
}

// Reset chat
if (clearChat) {
  clearChat.addEventListener("click", () => {
    chatStream.innerHTML = "";
    displayNpcMessage("Order history cleared! What would you like to know about Aditya?");
  });
}

// Service bell click
if (bellRing) {
  bellRing.addEventListener("click", () => {
    sfx.playBell();
    const bellQuotes = [
      "Ding! Order up! How can I help you today?",
      "Ding! Fresh espresso and code ready for review!",
      "Ding! Need a summary of Aditya's resume? Just ask below!"
    ];
    const quote = bellQuotes[Math.floor(Math.random() * bellQuotes.length)];
    if (baristaBubble) baristaBubble.querySelector(".speech-text").textContent = quote;
  });
}

// Typewriter effect
function typeWriter(element, text, speed = 16, callback) {
  element.textContent = "";
  let i = 0;
  function step() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      if (i % 3 === 0) sfx.playBlip();
      i++;
      setTimeout(step, speed);
    } else {
      if (callback) callback();
    }
    chatStream.scrollTop = chatStream.scrollHeight;
  }
  step();
}

// Append NPC Message
function displayNpcMessage(text, isTypewriter = true) {
  const msgDiv = document.createElement("div");
  msgDiv.className = "message npc-message";
  const bubble = document.createElement("div");
  bubble.className = "bubble-content";
  const p = document.createElement("p");
  bubble.appendChild(p);
  msgDiv.appendChild(bubble);
  chatStream.appendChild(msgDiv);
  if (isTypewriter) {
    typeWriter(p, text);
  } else {
    p.textContent = text;
  }
  chatStream.scrollTop = chatStream.scrollHeight;
}

// Append User Message
function displayUserMessage(text) {
  const msgDiv = document.createElement("div");
  msgDiv.className = "message user-message";
  const bubble = document.createElement("div");
  bubble.className = "bubble-content";
  bubble.textContent = text;
  msgDiv.appendChild(bubble);
  chatStream.appendChild(msgDiv);
  chatStream.scrollTop = chatStream.scrollHeight;
}

// Typing Indicator
function showTypingIndicator() {
  const indicator = document.createElement("div");
  indicator.id = "typingIndicator";
  indicator.className = "typing-indicator";
  indicator.innerHTML = `
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  `;
  chatStream.appendChild(indicator);
  chatStream.scrollTop = chatStream.scrollHeight;
}

function removeTypingIndicator() {
  const ind = document.getElementById("typingIndicator");
  if (ind) ind.remove();
}

// Send Chat Request to Backend
async function handleChat(question) {
  displayUserMessage(question);
  showTypingIndicator();

  if (baristaBubble) {
    baristaBubble.querySelector(".speech-text").textContent = "Brewing an answer for you...";
  }

  try {
    const response = await fetch(`${apiBase}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question })
    });

    removeTypingIndicator();

    if (!response.ok) throw new Error(`Server returned status ${response.status}`);

    const data = await response.json();
    const answer = data.answer || "I don't have enough information to answer that.";
    displayNpcMessage(answer);

    if (baristaBubble) {
      baristaBubble.querySelector(".speech-text").textContent = "Here's what I found!";
    }
  } catch (err) {
    removeTypingIndicator();
    console.error("Chat error:", err);
    displayNpcMessage(
      `Connection issue: Could not reach ${apiBase}/chat. Make sure your FastAPI server is running (uvicorn adi:app --reload). Click the gear icon below to change the URL.`
    );
    if (baristaBubble) {
      baristaBubble.querySelector(".speech-text").textContent = "Hmm, backend seems offline!";
    }
  }
}

// Form submit
if (chatForm) {
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = userInput.value.trim();
    if (!q) return;
    userInput.value = "";
    handleChat(q);
  });
}

// Quick Prompt Chips
document.querySelectorAll(".prompt-chip").forEach((btn) => {
  btn.addEventListener("click", () => {
    const query = btn.getAttribute("data-query");
    if (query) handleChat(query);
  });
});

// Chalkboard menu items → directly trigger Barista NPC dialogue
const menuQueries = {
  about: "Tell me about Aditya's background, education, and story.",
  skills: "What are Aditya's key technical skills, languages, and frameworks?",
  projects: "What notable projects and AI systems has Aditya built?",
  resume: "Can you provide a concise summary of Aditya's resume and experiences?",
  contact: "How can I contact or hire Aditya? What are his contact details?"
};

document.querySelectorAll(".chalk-item").forEach((item) => {
  const handleMenuClick = () => {
    const action = item.getAttribute("data-action");
    sfx.playBlip();
    if (action === "resume") {
      window.open("assets/resume.pdf", "_blank");
    }
    const query = menuQueries[action];
    if (query) handleChat(query);
  };

  item.addEventListener("click", handleMenuClick);
  item.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleMenuClick();
    }
  });
});
