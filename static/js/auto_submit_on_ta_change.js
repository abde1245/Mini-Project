document.addEventListener('DOMContentLoaded', function () {
    var taSelect = document.getElementById('id_ta');
    var form = document.querySelector('form');

    if (!taSelect || !form) {
        console.error('TA select or form not found.');
        return;
    }

    taSelect.addEventListener('change', function () {
        console.log('TA selection changed. Submitting form directly.');
        form.submit();
    });
});