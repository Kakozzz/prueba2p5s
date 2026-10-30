const API_URL = "http://35.86.130.100:8000";

async function shortenUrl() {
    const originalUrlInput = document.getElementById("originalUrl");
    const errorMsg = document.getElementById("errorMsg");
    const resultContainer = document.getElementById("resultContainer");
    const shortUrlOutput = document.getElementById("shortUrlOutput");
    const visitLink = document.getElementById("visitLink");

    errorMsg.classList.add("hidden");
    resultContainer.classList.add("hidden");
    errorMsg.innerText = "";

    const urlValue = originalUrlInput.value.trim();

    if (!urlValue) {
        showError("Por favor ingresa una URL válida.");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/shorten`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ original_url: urlValue })
        });

        if (!response.ok) {
            throw new Error("Error en el servidor al procesar la solicitud.");
        }

        const data = await response.json();
        
        const realShortUrl = `${API_URL}/${data.short_code}`;
        
        shortUrlOutput.value = realShortUrl;
        visitLink.href = realShortUrl;
        resultContainer.classList.remove("hidden");

    } catch (err) {
        showError("No se pudo conectar con el backend en EC2. Verifica que el servidor esté activo y CORS configurado.");
    }
}

function showError(message) {
    const errorMsg = document.getElementById("errorMsg");
    errorMsg.innerText = message;
    errorMsg.classList.remove("hidden");
}

function copyToClipboard() {
    const shortUrlOutput = document.getElementById("shortUrlOutput");
    shortUrlOutput.select();
    document.execCommand("copy");
    alert("¡Enlace copiado al portapapeles!");
}