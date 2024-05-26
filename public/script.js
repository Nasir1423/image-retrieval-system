document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    try {
        const response = await axios.post('/searchResult', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        const results = response.data.results;
        // 保存结果并重定向到结果页面
        localStorage.setItem('results', JSON.stringify(results));
        window.location.href = '/searchResult';
    } catch (error) {
        console.error('There was an error uploading the image!', error);
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');

    imageUpload.addEventListener('change', function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                imagePreview.style.display = 'block';
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Image Preview" style="width:100px">`;
            }
            reader.readAsDataURL(file);
        } else {
            imagePreview.style.display = 'none';
            imagePreview.innerHTML = '';
        }
    });
});

