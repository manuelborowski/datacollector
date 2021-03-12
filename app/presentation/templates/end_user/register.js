var formio_form
$(document).ready(function () {
    Formio.createForm(document.getElementById('register-form'), data.template).then((form) => {
        $.each(data.formio_data, function (k, v) {
            try {
                form.getComponent(k).setValue(v);
            } catch (error ) {
                return;
            }
        });
        formio_form = form
        form.on('submit', function(submitted) {
            window.location.href = Flask.url_for(registration_endpoint, {form_data: JSON.stringify(submitted.data)});
        });
    });
});
