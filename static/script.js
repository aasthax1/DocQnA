function uploadPDF() {
    let file = document.getElementById("pdfFile").files[0];
    if (!file) {
        alert("Please select a PDF file!");
        return;
    }

    let formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("uploadMsg").innerText = data.message;
    })
    .catch(err => console.error(err));
}

function askQuestion() {
    let question = document.getElementById("question").value;
    if (!question) {
        alert("Please type a question!");
        return;
    }

    fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("answer").innerText = data.answer;
    })
    .catch(err => console.error(err));
}
