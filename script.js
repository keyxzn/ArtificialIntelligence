document.getElementById("upload-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch("/predict", {
        method: "POST",
        body: formData,
    })
    .then((response) => response.json())
    .then((data) => {
        const resultDiv = document.getElementById("prediction-result");

        if (data.error) {
            resultDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
        } else {
            resultDiv.innerHTML = `
                <h3>Hasil Prediksi:</h3>
                <div id="original-image-container">
                    <h4>Gambar Asli:</h4>
                    <img id="original-img" src="${data.original_image_url}" alt="Original Image" style="max-width: 100%; height: auto;">
                </div>
                <div id="mask-image-container">
                    <h4>Mask Gambar:</h4>
                    <img id="mask-img" src="${data.mask_image_url}" alt="Mask Image" style="max-width: 100%; height: auto;">
                </div>
                <p>Persentase Deforestasi: ${data.deforested_percentage}</p>
            `;
        }
    })
    .catch((error) => {
        console.error("Error:", error);
    });
});


document.getElementById('predict-another-btn').addEventListener('click', function() {
    document.getElementById('upload-form').reset();
    document.getElementById('result').style.display = 'none';
    document.getElementById('predict-another-btn').style.display = 'none';

    this.reset();
});


document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("upload-form");
    const predictionResult = document.getElementById("prediction-result");
    const predictAnotherBtn = document.getElementById("predict-another-btn");

    const originalImageContainer = document.getElementById("original-image-container");
    const maskImageContainer = document.getElementById("mask-image-container");
    const originalImg = document.getElementById("original-img");
    const maskImg = document.getElementById("mask-img");
    const deforestedPercentage = document.getElementById("deforested-percentage");

    predictionResult.style.display = "none";
    predictAnotherBtn.style.display = "none";

    uploadForm.addEventListener("submit", (event) => {
        event.preventDefault();

        predictionResult.style.display = "none";
        predictAnotherBtn.style.display = "none";

        const formData = new FormData(uploadForm);

        fetch("/predict", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    alert("Error: " + data.error);
                } else {
                    originalImg.src = data.original_image_url;
                    maskImg.src = data.mask_image_url;
                    deforestedPercentage.textContent = `Persentase Deforestasi: ${data.deforested_percentage}`;
                    
                    predictionResult.style.display = "block";
                    predictAnotherBtn.style.display = "inline-block";
                }
            })
            .catch((error) => {
                console.error("Error:", error);
                alert("Terjadi kesalahan, silakan coba lagi.");
            });
    });

    
    predictAnotherBtn.addEventListener("click", () => {
        uploadForm.reset();
        predictionResult.style.display = "none";
        predictAnotherBtn.style.display = "none";
    });
});