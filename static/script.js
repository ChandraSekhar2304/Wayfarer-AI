let currentThreadId = localStorage.getItem("wayfarer_thread_id") || null;
let latestAnswerMarkdown = "";

function setPrompt(text) {
    document.getElementById("userInput").value = text;
}

function setLoading(isLoading) {
    const sendBtn = document.getElementById("sendBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");

    sendBtn.disabled = isLoading;

    if (isLoading) {
        btnText.classList.add("hidden");
        btnLoader.classList.remove("hidden");
    } else {
        btnText.classList.remove("hidden");
        btnLoader.classList.add("hidden");
    }
}

function showError(message) {
    const errorBox = document.getElementById("errorBox");

    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function hideError() {
    const errorBox = document.getElementById("errorBox");

    errorBox.classList.add("hidden");
    errorBox.textContent = "";
}

function showResult(answer, threadId) {
    latestAnswerMarkdown = answer;

    const resultSection = document.getElementById("resultSection");
    const resultBox = document.getElementById("resultBox");
    const threadInfo = document.getElementById("threadInfo");

    if (typeof marked !== "undefined") {
        resultBox.innerHTML = marked.parse(answer);
    } else {
        resultBox.innerText = answer;
    }

    threadInfo.textContent = `Thread ID: ${threadId}`;

    resultSection.classList.remove("hidden");

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

let progressInterval = null;
let progressStartTime = null;

const UNIFORM_STAGES = [
    { startSec: 0, endSec: 7.5, title: "✈️ Flight Agent Active", desc: "Analyzing airlines, routes, and airport options...", minP: 5, maxP: 24 },
    { startSec: 7.5, endSec: 15, title: "🏨 Hotel Agent Searching", desc: "Querying Tavily MCP for top-rated hotels in your budget...", minP: 24, maxP: 46 },
    { startSec: 15, endSec: 22.5, title: "🌤 Weather Agent Checking", desc: "Fetching live weather conditions and 5-day forecasts...", minP: 46, maxP: 68 },
    { startSec: 22.5, endSec: 30, title: "📝 Itinerary Agent Planning", desc: "Structuring day-by-day activities and travel logistics...", minP: 68, maxP: 86 },
    { startSec: 30, endSec: 38, title: "✨ Final Agent Assembling", desc: "Finalizing budget, schedules, and travel recommendations...", minP: 86, maxP: 96 }
];

function startProgressAnimation() {
    const progressBox = document.getElementById("progressBox");
    const title = document.getElementById("progressStepTitle");
    const desc = document.getElementById("progressStepDesc");
    const fill = document.getElementById("progressBarFill");

    if (!progressBox) return;

    progressBox.classList.remove("hidden");
    progressStartTime = Date.now();

    if (progressInterval) clearInterval(progressInterval);

    progressInterval = setInterval(() => {
        const elapsed = (Date.now() - progressStartTime) / 1000;
        let currentStage = UNIFORM_STAGES.find(s => elapsed >= s.startSec && elapsed < s.endSec);

        if (currentStage) {
            title.textContent = currentStage.title;
            desc.textContent = currentStage.desc;
            const stageProgress = (elapsed - currentStage.startSec) / (currentStage.endSec - currentStage.startSec);
            const currentPct = currentStage.minP + stageProgress * (currentStage.maxP - currentStage.minP);
            fill.style.width = `${Math.min(currentPct, 96)}%`;
        } else if (elapsed >= 38) {
            title.textContent = "✨ Final Agent Assembling";
            desc.textContent = "Polishing final travel plan and budget summary...";
            const extra = Math.min((elapsed - 38) / 15, 1) * 2.5;
            fill.style.width = `${96 + extra}%`;
        }
    }, 200);
}

function stopProgressAnimation() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    const fill = document.getElementById("progressBarFill");
    const progressBox = document.getElementById("progressBox");
    if (fill) fill.style.width = "100%";
    setTimeout(() => {
        if (progressBox) progressBox.classList.add("hidden");
    }, 350);
}

async function sendMessage() {
    hideError();

    const input = document.getElementById("userInput");
    const message = input.value.trim();

    if (!message) {
        showError("Please enter your travel request first.");
        return;
    }

    setLoading(true);
    startProgressAnimation();

    try {
        const response = await fetch("/api/travel", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                thread_id: currentThreadId
            })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Something went wrong.");
        }

        currentThreadId = data.thread_id;
        localStorage.setItem("wayfarer_thread_id", currentThreadId);

        showResult(data.answer, data.thread_id);

    } catch (error) {
        showError(error.message);
    } finally {
        stopProgressAnimation();
        setLoading(false);
    }
}

function copyResult() {
    const resultBox = document.getElementById("resultBox");
    const text = resultBox.innerText;

    if (!text) {
        return;
    }

    navigator.clipboard.writeText(text)
        .then(() => {
            const copyBtn = document.querySelector(".copy-btn");
            const oldText = copyBtn.textContent;

            copyBtn.textContent = "Copied!";

            setTimeout(() => {
                copyBtn.textContent = oldText;
            }, 1400);
        })
        .catch(() => {
            showError("Could not copy result.");
        });
}

function downloadPDF() {
    const pdfContent = document.getElementById("pdfContent");

    if (!latestAnswerMarkdown || !pdfContent) {
        showError("No travel plan available to download.");
        return;
    }

    const downloadBtn = document.querySelector(".download-btn");
    const oldText = downloadBtn.textContent;

    downloadBtn.textContent = "Preparing PDF...";
    downloadBtn.disabled = true;

    const options = {
        margin: 0.5,
        filename: "ai-travel-plan.pdf",
        image: {
            type: "jpeg",
            quality: 0.98
        },
        html2canvas: {
            scale: 2,
            useCORS: true,
            backgroundColor: "#ffffff"
        },
        jsPDF: {
            unit: "in",
            format: "a4",
            orientation: "portrait"
        },
        pagebreak: {
            mode: ["avoid-all", "css", "legacy"]
        }
    };

    html2pdf()
        .set(options)
        .from(pdfContent)
        .save()
        .then(() => {
            downloadBtn.textContent = oldText;
            downloadBtn.disabled = false;
        })
        .catch(() => {
            downloadBtn.textContent = oldText;
            downloadBtn.disabled = false;
            showError("Could not download PDF.");
        });
}

document.addEventListener("keydown", function(event) {
    if (event.ctrlKey && event.key === "Enter") {
        sendMessage();
    }
});