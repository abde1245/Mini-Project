var $ = django.jQuery || window.jQuery;

$(document).ready(function() {
    var roleField = $('#id_role');
    
    // Select the fieldset elements directly using their classes
    var studentFields = $('fieldset.student-fields-class'); 
    var facultyFields = $('fieldset.faculty-fields-class');

    // Check if elements are found (for debugging)
    // console.log("Role field:", roleField.length > 0);
    // console.log("Student fields found:", studentFields.length > 0);
    // console.log("Faculty fields found:", facultyFields.length > 0);

    function toggleRoleSpecificFields() {
        var selectedRoleText = roleField.find('option:selected').text().trim().toLowerCase();
        // console.log("Selected Role Text:", selectedRoleText);

        studentFields.hide();
        facultyFields.hide();

        if (selectedRoleText === 'student') {
            studentFields.show();
        } else if (selectedRoleText === 'faculty') {
            facultyFields.show();
        }
    }

    roleField.on('change', toggleRoleSpecificFields);
    toggleRoleSpecificFields(); // Initial call
});