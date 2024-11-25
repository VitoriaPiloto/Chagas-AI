function uploadFile(event) {
    event.preventDefault();
    
    var formData = new FormData();
    var fileInput = document.getElementById("fileInput");
    formData.append("file", fileInput.files[0]);

    // Fazer a requisição AJAX para enviar o arquivo
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:5000/upload", true);

    xhr.onload = function() {
        if (xhr.status === 200) {
            // Exibir o resultado na página
            document.getElementById("result").innerHTML = xhr.responseText;
        } else {
            alert('Erro ao enviar o arquivo!');
        }
    };

    xhr.send(formData);
}
