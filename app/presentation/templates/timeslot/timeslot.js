var _form = null;
var timeslot_component = null;
$(document).ready(function () {
    Formio.createForm(document.getElementById('timeslot-settings'), data.template).then((form) => {
        _form = form;
        timeslot_component = form.getComponent("timeslot-list");

        timeslot_component.setValue(data.timeslots);
        form.on('submit', function(submission) {
            window.location.href = Flask.url_for(registration_endpoint, {form_data: JSON.stringify(submitted.data)});
        })
        $("[ref=datagrid-timeslot-list-row]").on("click", function(e) {
            var row_index = e.currentTarget.rowIndex;
            timeslot_component.rows[row_index - 1]['timeslot-action'].setValue('U');
        })
    });
});
