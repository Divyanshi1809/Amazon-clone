document.getElementById('checkBtn').addEventListener('click', async () => {
    const city = document.getElementById('cityInput').value.trim();
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '';

    if (!city) {
        resultDiv.innerHTML = `<div class="alert alert-danger">Please enter a city name.</div>`;
        return;
    }

    try {
        const res = await fetch('/get_aqi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city })
        });

        const data = await res.json();

        if (res.ok) {
            const aqi = data.overall_aqi;
            resultDiv.innerHTML = `<div class="alert alert-info">AQI for <strong>${city}</strong>: <strong>${aqi}</strong></div>`;
        } else {
            resultDiv.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
        }
    } catch (err) {
        resultDiv.innerHTML = `<div class="alert alert-danger">Unexpected error occurred: ${err.message}</div>`;
    }
});
