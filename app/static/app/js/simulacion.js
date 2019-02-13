var simulacion = function() {
    'use strict';
    return {
        init: function() {
            initNuevoProcesoForm();
            initEliminarProcesoForm();
            initParamsForm();
            initSimulacionForm();
        }
    };
}();

var dataSim = {
    'pid': 0
}

var initNuevoProcesoForm = function() {
    $('form[name="nuevo_proceso"]').submit(function(e) {
        e.preventDefault();
        // Validamos las ráfagas con una regex
        var rafagas = checkBursts($('input[name="rafagas"]', this).val().trim());
        if (rafagas) {
            $('#error-rafagas > p.error-mensaje').text(rafagas);
            $('#error-rafagas').fadeIn();
        } else {
            $('#error-rafagas').fadeOut();
            // Incrementamos el numero de proceso
            dataSim.pid += 1;
            // Agregamos el proceso a la tabla
            addRow(
                dataSim.pid,
                $('input[name="descripcion"]', this).val().trim(),
                $('input[name="ta"]', this).val(),
                $('input[name="rafagas"]', this).val().trim(),
                $('input[name="memoria"]', this).val().trim()
            );
            checkProcessNumer();
            // Reiniciamos el formulario
            if ($('#otro-proceso').prop('checked')) {
                $('#nuevoProcesoModal').trigger('shown.bs.modal').trigger('hidden.bs.modal');
            } else {
                $('#nuevoProcesoModal').modal('hide');
            }
        }
    });

    $('#nuevoProcesoModal').on('shown.bs.modal', function (e) {
        $('input[name="descripcion"]', this).focus();
    });

    $('#nuevoProcesoModal').on('hidden.bs.modal', function (e) {
        $('form[name="nuevo_proceso"]').trigger('reset');
    });

    $('#nav-particion-fija').click(function(e) {
        $('#div-fijas').show();
        $('input[name="partes_fijas"]').removeAttr('disabled');
        $('#memoria').attr('disabled', 'disabled');
        $('#div-variables').hide();
    });

    $('#nav-particion-variable').click(function(e) {
        $('#div-variables').show();
        $('#memoria').removeAttr('disabled');
        $('input[name="partes_fijas"]').attr('disabled', 'disabled');
        $('#div-fijas').hide();
    });
};

var addRow = function(pid, descripcion, ta, rafagas,memoria) {
    $('#tabla-procesos > tbody:last-child').append(`
        <tr id="proceso-`+pid+`" data-id="`+pid+`" data-descripcion="`+descripcion+`" data-ta="`+ta+`" data-rafagas="`+rafagas+`" data-memoria="`+memoria+`" class="item-proceso">
            <th scope="row">`+pid+`</th>
            <td>`+descripcion+`</td>
            <td>`+ta+`</td>
            <td>`+rafagas.split(',').join(' - ')+`</td>
        </tr>
    `);
};

var checkBursts = function(rafagas) {
    if (rafagas.match(/^\d+(?:,\d+)*$/)) {
        if (rafagas.split(',').length % 2 == 0) {
            return 'El número de ráfagas debe ser impar terminando siempre con una ráfaga de CPU.';
        }
        return false;
    }
    return 'El formato ingresado en las ráfagas CPU - E/S es inválido.';
};

var initEliminarProcesoForm = function() {
    $('#eliminarProcesoModal').on('show.bs.modal', function(e) {
        $('.item-eliminar').remove();
        $('.item-proceso').each(function(idx, elem) {
            addRowToDelete(
                $(this).data('id'),
                $(this).data('descripcion')
            );
        });
    });

    $('#eliminar_todos').change(function() {
        var checkboxes = $(this).closest('form').find(':checkbox');
        checkboxes.prop('checked', $(this).is(':checked'));
    });

    $('form[name="eliminar_procesos"]').submit(function(e) {
        e.preventDefault();
        $('.item-eliminar-checkbox:checked').each(function(idx, elem) {
            var row = $(this).parent().parent();
            $('#proceso-'+$(row).data('pid')).remove();
            row.remove();
        });
        checkProcessNumer();
        $('#eliminarProcesoModal').modal('hide');
    });
};

var addRowToDelete = function(pid, descripcion) {
    $('#tabla-eliminar-procesos > tbody:last-child').append(`
        <tr data-pid="`+pid+`" data-descripcion="`+descripcion+`" class="item-eliminar">
            <th scope="row">`+pid+`</th>
            <td>`+descripcion+`</td>
            <td>
                <input type="checkbox" class="item-eliminar-checkbox">
            </td>
        </tr>
    `);
};

var checkProcessNumer = function() {
    if ($('.item-proceso').length) {
        $('.sin-procesos').hide();
        $('#iniciar-simulacion').removeAttr('disabled');
    } else {
        $('.sin-procesos').show();
        $('#iniciar-simulacion').attr('disabled', true);
    }
}

var initSimulacionForm = function() {
    $('#iniciar-simulacion').click(function(e) {
        e.preventDefault();

        $('.item-proceso').each(function(idx, elem) {
            saveProceso(this);
        });

        $('#simulacion').submit();
    })
}

var saveProceso = function(proceso) {
    var pData = [$(proceso).data('id'), $(proceso).data('descripcion'), $(proceso).data('ta'), $(proceso).data('rafagas'), $(proceso).data('memoria')].join('-');
    $('#simulacion').prepend('<input type="hidden" name="procesos" value="'+pData+'">');
}

var initParamsForm = function() {
    $('form[name="editar_parametros"]').submit(function(e) {
        e.preventDefault();
        $('#input-quantum').val($('#quantum').val());
        $('#input-memoria').val($('#memoria').val());
        $('#input-partes-fijas').val($('#partes_fijas').val());
        $('#paramsModal').modal('hide');
    });
};
