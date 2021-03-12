var _form = null;
var timeslot_component = null;

$(document).ready(function () {
    socketio.start(null, null);
    socketio.subscribe_on_receive("settings", socketio_receive_settings);
    Formio.createForm(document.getElementById('configuration-settings'), data.template).then((form) => {
        _form = form
        $.each(data.default, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error) {
                return;
            }
        });
        timeslot_component = form.getComponent("timeslot-list");
        timeslot_component.setValue(data.timeslots);
        form.on('submit', function(submission) {
            socketio_transmit_setting('data', JSON.stringify((submission.data)))
        })
        $('.formio-component-panel [ref=header]').on('click', panel_header_clicked);
    });
});


function socketio_receive_settings(type, data) {
    _form.emit('submitDone')
    setTimeout(function() {$("#configuration-settings .alert").css("display", "none");}, 1000);
    if (!data.status) {
        bootbox.alert("Opgepast, er is volgende fout opgetreden:<br>" + data.message);
    }

}


function socketio_transmit_setting(setting, value) {
    socketio.send_to_server('settings', {setting: setting, value: value});
    return false;
}

function panel_header_clicked(event) {
    event.stopImmediatePropagation();
    $("[ref=datagrid-timeslot-list-row]").on("change", function(e) {
        var row_index = e.currentTarget.rowIndex;
        timeslot_component.rows[row_index - 1]['timeslot-action'].setValue('U');
    })
    $('.formio-component-panel  [ref=header]').on('click', panel_header_clicked);
}
