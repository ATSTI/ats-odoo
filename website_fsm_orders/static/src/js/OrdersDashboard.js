$(document).ready(function () {
    var dashboardEl = document.getElementById('agenda-dashboard');
    if (!dashboardEl) return;

    var MESES = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                 'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'];
    var DIAS  = ['Domingo','Segunda-feira','Terça-feira','Quarta-feira',
                 'Quinta-feira','Sexta-feira','Sábado'];

    function parseDate(str) {
        if (!str) return new Date(NaN);
        // Substitui espaço por T: "2026-05-26 12:00:00" → "2026-05-26T12:00:00"
        return new Date(str.replace(' ', 'T'));
    }


    function formatarDia(dt) {
        return DIAS[dt.getDay()] + ', ' +
               dt.getDate() + ' de ' +
               MESES[dt.getMonth()];
    }

    function formatarHora(str, allDay) {
        if (allDay) return 'Dia inteiro';
        var dt = parseDate(str);
        return dt.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }

    function ehHoje(dt) {
        var hoje = new Date();
        return dt.getDate() === hoje.getDate() &&
               dt.getMonth() === hoje.getMonth() &&
               dt.getFullYear() === hoje.getFullYear();
    }

    function ehAmanha(dt) {
        var amanha = new Date();
        amanha.setDate(amanha.getDate() + 1);
        return dt.getDate() === amanha.getDate() &&
               dt.getMonth() === amanha.getMonth() &&
               dt.getFullYear() === amanha.getFullYear();
    }

    function badgeDia(dt) {
        if (ehHoje(dt))   return '<span class="agenda-badge hoje">Hoje</span>';
        if (ehAmanha(dt)) return '<span class="agenda-badge amanha">Amanhã</span>';
        return '';
    }

    function renderizarGrupos(eventos) {
        // Agrupa por data
        var grupos = {};
        eventos.forEach(function(ev) {
            var dt = parseDate(ev.start);
            var chave = dt.getFullYear() + '-' +
                        String(dt.getMonth()).padStart(2,'0') + '-' +
                        String(dt.getDate()).padStart(2,'0');
            if (!grupos[chave]) grupos[chave] = { dt: dt, eventos: [] };
            grupos[chave].eventos.push(ev);
        });

        var chaves = Object.keys(grupos).sort();
        var html = '';

        chaves.forEach(function(chave) {
            var grupo = grupos[chave];
            var dt = grupo.dt;
            var isHoje = ehHoje(dt);

            html += '<div class="agenda-grupo' + (isHoje ? ' grupo-hoje' : '') + '">';
            html += '<div class="agenda-grupo-header">';
            html += '<span class="agenda-grupo-dia">' + formatarDia(dt) + '</span>';
            html += badgeDia(dt);
            html += '</div>';
            html += '<div class="agenda-cards">';

            grupo.eventos.forEach(function(ev) {
                var horaInicio = formatarHora(ev.start, ev.allDay);
                var horaFim    = ev.allDay ? '' : formatarHora(ev.end, false);
                var horario    = ev.allDay ? 'Dia inteiro' : horaInicio + ' – ' + horaFim;

                html += '<div class="agenda-card">';
                html += '  <div class="agenda-card-hora">' + horario + '</div>';
                html += '  <div class="agenda-card-titulo">' + ev.title + '</div>';

                if (ev.location) {
                    html += '  <div class="agenda-card-local">📍 ' + ev.location + '</div>';
                }
                if (ev.description) {
                    html += '  <div class="agenda-card-desc">' + ev.description + '</div>';
                }

                html += '</div>';
            });

            html += '</div></div>';
        });

        return html || '<div class="agenda-vazio">Nenhum compromisso nos próximos 30 dias.</div>';
    }

    function atualizarKPIs(eventos) {
        var hoje = new Date();
        var semanaFim = new Date();
        semanaFim.setDate(hoje.getDate() + 7);

        var semana = eventos.filter(function(ev) {
            var dt = parseDate(ev.start);
            return dt >= hoje && dt <= semanaFim;
        });

        $('#kpi-total').text(eventos.length);
        $('#kpi-semana').text(semana.length);

        var proximo = eventos.filter(function(ev) {
            return parseDate(ev.start) >= hoje;
        })[0];

        if (proximo) {
            var dt = parseDate(proximo.start);
            $('#kpi-proximo-titulo').text(proximo.title);
            $('#kpi-proximo-data').text(
                ehHoje(dt) ? 'Hoje, ' + formatarHora(proximo.start, proximo.allDay)
                           : formatarDia(dt)
            );
        } else {
            $('#kpi-proximo-titulo').text('—');
            $('#kpi-proximo-data').text('Nenhum compromisso pendente');
        }
    }

    // Carrega os eventos
    $('#agenda-loading').show();
    $('#agenda-dashboard').hide();

    fetch('/agenda/eventos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: "2.0", method: "call", params: {} })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        var eventos = data.result || [];
        atualizarKPIs(eventos);
        document.getElementById('agenda-lista').innerHTML = renderizarGrupos(eventos);
        $('#agenda-loading').hide();
        $('#agenda-dashboard').show();
    })
    .catch(function(err) {
        console.error('Erro ao carregar eventos:', err);
        $('#agenda-loading').hide();
        $('#agenda-erro').show();
    });
});