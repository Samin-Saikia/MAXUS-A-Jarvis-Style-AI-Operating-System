
    let jarvisVoice = null;
   // ✅ ADD THIS
    // 1. Create an array of Jarvis-inspired lines
const jarvisLines = [
    " ALL System ready. All parameters nominal . responce delivered.",
    "Good morning, sir. output proccesed.",
    "BOSS i processed the output. Information retrieval in progress.",
    "Analysis complete. The results are in your display panel.",
    
    "All internal systems functioning optimally, input to output loop is fine, waiting for you BOSS.",
    "User authentication successful. Welcome back BOSS , requests delivered waiting for youe responce.",
    "Activating heads-up display sir .",
    "Energy levels at one hundred percent . output processed in you screen.",
    "Protocol initiated. Task execution completed ."
];

// 2. Function to select a random line from the array
function getRandomJarvisLine() {
    // Generate a random index based on the array length
    const randomIndex = Math.floor(Math.random() * jarvisLines.length);
    // Return the element at the random index
    return jarvisLines[randomIndex];
}

    // Clock
    function updateClock() {
      const now = new Date();
      let h = now.getHours();
      const m = String(now.getMinutes()).padStart(2, '0');
      const s = String(now.getSeconds()).padStart(2, '0');
      const ampm = h >= 12 ? 'PM' : 'AM';
      h = h % 12 || 12;
      document.getElementById('clock').textContent = `${h}:${m}:${s} ${ampm}`;
    }
    setInterval(updateClock, 1000);
    updateClock();


    /**
     * Speaks the provided text using a specific male voice if available.
     * @param {string} text The text to be spoken.
     */


// Load voices properly
function loadJarvisVoice() {
    const voices = window.speechSynthesis.getVoices();

    jarvisVoice =
        voices.find(v => v.name.includes("Google UK English Male")) ||
        voices.find(v => v.name.includes("Google US English")) ||
        voices.find(v => v.lang === "en-GB") ||
        voices.find(v => v.lang === "en-US") ||
        voices[0];
}

// Some browsers load voices late
window.speechSynthesis.onvoiceschanged = loadJarvisVoice;

// Call once manually too
loadJarvisVoice();

function speakJarvis(text) {
    if (!text) return;
    let cleanedText = text.replace(/[*#`]/g, '');
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(cleanedText);



    if (jarvisVoice) {
        utterance.voice = jarvisVoice;
    }

    utterance.rate = 1.0;   // calm
    utterance.pitch = 0.6; // deeper
    utterance.volume = 1;
    window.speechSynthesis.speak(utterance);

}


    // Mic toggle
// Move these variables outside the function so they persist between calls
let micActive = false;
let recognition = null;
let finalTranscript = ''; // Persist text across sessions

function toggleMic() {
    micActive = !micActive;
    const micBtn = document.getElementById('micBtn');
    const chatInput = document.getElementById('chatInput');
    // const bars = document.querySelectorAll('.bar'); // Optional

    if (micActive) {
        micBtn.classList.add('active');
        // bars.forEach(b => b.style.animationPlayState = 'running');

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SR();
            
            // --- KEY CHANGES HERE ---
            recognition.continuous = true; // Keep listening even if I pause
            recognition.interimResults = true; // Show text while speaking
            
            recognition.onresult = (e) => {
                let interimTranscript = '';
                for (let i = e.resultIndex; i < e.results.length; ++i) {
                    if (e.results[i].isFinal) {
                        finalTranscript += e.results[i][0].transcript + ' ';
                    } else {
                        interimTranscript += e.results[i][0].transcript;
                    }
                }
                // Update textarea with finalized text + current interim text
                chatInput.value = finalTranscript + interimTranscript;
            };

            recognition.onerror = (e) => {
                console.error(e);
                toggleMic(); // Stop on error
            };
            
            recognition.onend = () => {
                if (micActive) recognition.start(); // Keep restarting if mic is still "on"
            };

            recognition.start();
        } else {
            alert("Web Speech API not supported in this browser.");
            micActive = false;
        }
    } else {
        micBtn.classList.remove('active');
        if (recognition) {
            recognition.stop();
            // Optional: Store the new final value somewhere or just leave it in textarea
            finalTranscript = chatInput.value + ' '; 
            recognition = null;
        }
    }
}



    // Send message
    async function sendMessage() {
      console.log("sendMessage triggered");
      const input = document.getElementById('chatInput');
      const text = input.value.trim();
      if (!text) return;

      addMessage('YOU', text, 'user');
      input.value = '';

      const thinkingDiv = addMessage('MAXUS', 'Processing...');

      let response;

      try {
        response = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
      } catch (error) {
        console.error("Fetch error:", error);

        if (thinkingDiv?.isConnected) thinkingDiv.remove();

        // Do NOT show connection message
      }

      if (!response.ok) {
        if (thinkingDiv?.isConnected) thinkingDiv.remove();
        addMessage('MAXUS', 'Server error occurred.');
        return;
      }

      const data = await response.json();

      if (thinkingDiv?.isConnected) thinkingDiv.remove();

      addMessage('MAXUS', data.reply);
      const selectedResponse = getRandomJarvisLine();
      speakJarvis(data.reply);
    }

    function handleKey(e) {
      if (e.key === 'Enter') sendMessage();
    }

    function addMessage(sender, text, type = '') {
      const msgs = document.getElementById('messages');
      const div = document.createElement('div');
      div.className = 'message' + (type === 'user' ? ' user' : '');
      const now = new Date();
      let h = now.getHours() % 12 || 12;
      const m = String(now.getMinutes()).padStart(2, '0');
      const ampm = now.getHours() >= 12 ? 'PM' : 'AM';

      const renderedMarkdown = marked.parse(text);

      div.innerHTML = `
      <div class="msg-sender">${sender}</div>
      <div class="msg-content">${renderedMarkdown}</div>
      <div class="msg-time">${h}:${m} ${ampm}</div>
    `;


      msgs.appendChild(div);
      msgs.scrollTop = msgs.scrollHeight;
      
      if (window.MathJax) {
        MathJax.typesetPromise([div]);
      }

      return div; // 🔥 THIS IS IMPORTANT
    }

    function clearMessages() {
      const msgs = document.getElementById('messages');
      msgs.innerHTML = '';
      addMessage('MAXUS', 'Conversation cleared. Ready for new session.');
    }

    async function triggerSearch() {
  const input = document.getElementById('chatInput');
  const q = input.value.trim();

  if (!q) {
    addMessage('MAXUS', 'Web search mode activated. Enter your query.');
    return;
  }

  addMessage('MAXUS', `Initiating web search for: "${q}"...`);

  const response = await fetch('/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: q })
  });

  const data = await response.json();
  addMessage('MAXUS', data.reply);
  speakJarvis(data.reply)
}

 async function handleImageUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const input = document.getElementById('chatInput');
  let question = input.value.trim();

  if (!question) {
    question = "Describe this image.";
  }

  addMessage('YOU', `[Image uploaded: ${file.name}]`, 'user');
  addMessage('YOU', question, 'user');

  input.value = '';

  const thinkingDiv = addMessage('MAXUS', 'Analyzing image...');

  const formData = new FormData();
  formData.append("image", file);
  formData.append("prompt", question);

  try {
    const response = await fetch("/vision", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    if (thinkingDiv?.isConnected) thinkingDiv.remove();

    addMessage('MAXUS', data.reply);
    speakJarvis(getRandomJarvisLine());

  } catch (error) {
    if (thinkingDiv?.isConnected) thinkingDiv.remove();
    addMessage('MAXUS', "Image processing failed.");
  }
}

    // Floating particles
    function createParticle() {
      const p = document.createElement('div');
      p.className = 'particle';
      p.style.left = Math.random() * 100 + 'vw';
      p.style.animationDuration = (8 + Math.random() * 12) + 's';
      p.style.animationDelay = Math.random() * 5 + 's';
      p.style.opacity = Math.random() * 0.5;
      document.body.appendChild(p);
      setTimeout(() => p.remove(), 20000);
    }

    setInterval(createParticle, 800);
    
    document.addEventListener("click", function initVoice() {
    const greeting = "Welcome sir. All systems activated. Waiting for your move.";

    speakJarvis(greeting);

    document.removeEventListener("click", initVoice);
});
function openYouTube() {
  // Opens a new blank window (default behavior)
  window.open('https://www.youtube.com/', '_blank');
}
function openGitHub(){
  window.open('https://github.com/', '_blank')
}
function openGoogle() {
  window.open("https://www.google.com", "_blank");
}
function openLinkedIn() {
  window.open("https://www.linkedin.com", "_blank");
  
  // Or open your profile
  // window.open("https://www.linkedin.com/in/your-profile", "_blank");
}

async function generatePdf() {
    const { jsPDF } = window.jspdf;

    const doc = new jsPDF({
        orientation: 'p',
        unit: 'pt',
        format: 'a4'
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    const margin = 50;
    const maxWidth = pageWidth - margin * 2;
    let y = margin;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(12);

    const messages = document.querySelectorAll(".message");

    for (let message of messages) {

        // Extract text content cleanly
        const text = message.innerText;

        // Wrap text to fit page width
        const splitText = doc.splitTextToSize(text, maxWidth);

        // If text exceeds page, add new page
        if (y + splitText.length * 14 > pageHeight - margin) {
            doc.addPage();
            y = margin;
        }

        doc.text(splitText, margin, y);
        y += splitText.length * 14 + 10;

        // Handle links inside message
        const links = message.querySelectorAll("a");
        for (let link of links) {
            const url = link.href;
            const linkText = link.innerText;

            if (y + 14 > pageHeight - margin) {
                doc.addPage();
                y = margin;
            }

            doc.setTextColor(0, 0, 255);
            doc.textWithLink(linkText, margin, y, { url });
            doc.setTextColor(0, 0, 0);

            y += 20;
        }

        y += 10; // spacing between messages
    }

    doc.save("chat-export.pdf");
}





// Example usage:
// openChrome(); 

