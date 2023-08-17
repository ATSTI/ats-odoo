  // function abrir() {
  //     document.getElementById('popup').style.display = 'block';
  // }
  function fechar() {
      document.getElementById('popup').style.display = 'none';
    }
  function fecharerror() {
      document.getElementById('popuperror').style.display = 'none';
      document.getElementById('popup').style.display = 'block';
  }

  function confirmar() {
      document.getElementById('popup').style.display = 'none';
      var selectedOption = document.getElementById('inlinesOptions').value;
      if (selectedOption === '') {
        document.getElementById('popuperror').style.display = 'block';
      }
      if (selectedOption === '0') {
        document.getElementById('popuperror').style.display = 'block';
      }
      else {
        document.getElementById('test').innerText = selectedOption + ' Parcelas';
        document.getElementById('test').style.background = '#73ca9f';
        document.getElementById('test').style.border = 'solid 2px #79a490';
      }
      
    }
