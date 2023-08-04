  function abrircheck() {
      document.getElementById('popupcheck').style.display = 'block';
    }
  function abrir() {
      document.getElementById('popup').style.display = 'block';
//      document.getElementById('popupcheck').style.display = 'none';
    //   for (i = 0; i < document.forms.selecao.elements.length; i++)
    //   if (document.forms.selecao.elements[i].type == "checkbox")
    //     document.forms.selecao.elements[i].checked = false;
  }
  function fecharCheck() {
      document.getElementById('popupcheck').style.display = 'none';
      for (i = 0; i < document.forms.selecao.elements.length; i++)
      if (document.forms.selecao.elements[i].type == "checkbox")
        document.forms.selecao.elements[i].checked = false;
    }
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
      else {
        document.getElementById('test').innerText = selectedOption + ' Parcelas';
        document.getElementById('test').style.background = '#73ca9f';
        document.getElementById('test').style.border = 'solid 2px #79a490';
      }
      
    }
