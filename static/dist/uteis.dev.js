"use strict";

function uploadFile(event) {
  event.preventDefault();
  var formData = new FormData();
  var fileInput = document.getElementById("fileInput");
  formData.append("file", fileInput.files[0]); // Fazer a requisição AJAX para enviar o arquivo

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/upload", true);

  xhr.onload = function () {
    if (xhr.status === 200) {
      // Agora a resposta está no formato JSON e pode ser analisada
      var response = JSON.parse(xhr.responseText);
      document.getElementById("result").innerHTML = "\n                <p><strong>Diagn\xF3stico:</strong> ".concat(montarMensagem(response.diagnostico), "</p>\n                <p><strong>Probabilidade:</strong> ").concat((response.probabilidade * 100).toFixed(2), "%</p>\n                <button onclick=\"prepareFeedback('").concat(fileInput.files[0].name, "')\">Dar Feedback</button>\n            ");
    } else {
      alert('Erro ao enviar o arquivo!');
    }
  };

  xhr.send(formData);
}

function montarMensagem(diagnostico) {
  if (diagnostico == 'positivo') return "Existe muita chance de conter a doença de chagas! Procure um médico!";
  if (diagnostico == 'pode ter') return "Existe a possibilidade de conter a doença";
  if (diagnostico == 'negativo') return "Não possui a doença";
}

function prepareFeedback(fileName) {
  // Mostrar o formulário de feedback
  document.getElementById("feedback-arquivo").innerText = fileName;
  document.getElementById("feedback-form").style.display = "block";
}

function enviarFeedback() {
  var arquivoNome = document.getElementById("feedback-arquivo").innerText;
  var diagnosticoReal = document.getElementById("diagnostico-real").value;
  fetch('/feedback', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      arquivo_nome: arquivoNome,
      diagnostico_real: diagnosticoReal
    })
  }).then(function (res) {
    return res.json();
  }).then(function (data) {
    alert(data.message); // Esconder o formulário após o envio

    document.getElementById("feedback-form").style.display = "none";
  })["catch"](function (err) {
    alert('Erro ao enviar feedback!');
    console.error(err);
  });
}