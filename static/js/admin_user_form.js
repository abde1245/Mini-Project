// static/js/admin_user_form.js
document.addEventListener('DOMContentLoaded', function() {
    var roleSelect = document.getElementById('id_role'); // Adjust ID if necessary

    if (roleSelect) {
        var studentFields = document.querySelectorAll('.student-fields-class'); // Use the class names from admin.py
        var facultyFields = document.querySelectorAll('.faculty-fields-class'); // Use the class names from admin.py

        function toggleRoleFields() {
            var selectedRoleId = roleSelect.value;
            // Get the selected role name based on the option text or data attribute
            var selectedRoleName = roleSelect.options[roleSelect.selectedIndex].text;
            console.log("Selected Role Name:", selectedRoleName); // Debugging

            // Show/hide based on role name (more readable)
            if (selectedRoleName === 'Student') {
                studentFields.forEach(function(fieldset) { fieldset.style.display = 'block'; });
                facultyFields.forEach(function(fieldset) { fieldset.style.display = 'none'; });
            } else if (selectedRoleName === 'Faculty') {
                studentFields.forEach(function(fieldset) { fieldset.style.display = 'none'; });
                facultyFields.forEach(function(fieldset) { fieldset.style.display = 'block'; });
            } else { // Admin or other roles
                studentFields.forEach(function(fieldset) { fieldset.style.display = 'none'; });
                facultyFields.forEach(function(fieldset) { fieldset.style.display = 'none'; });
            }

            // Optional: Clear values when hiding fields to prevent saving unwanted data
            // This is less necessary with the form.save override clearing data, but can be a safety measure.
            if (selectedRoleName !== 'Student') {
                studentFields.forEach(function(fieldset) {
                    fieldset.querySelectorAll('input, select, textarea').forEach(function(input) { input.value = ''; });
                });
            }
            if (selectedRoleName !== 'Faculty') {
                facultyFields.forEach(function(fieldset) {
                    fieldset.querySelectorAll('input, select, textarea').forEach(function(input) { input.value = ''; });
                });
            }
        }

        // Initial state on page load
        toggleRoleFields();

        // Bind event listener to role change
        roleSelect.addEventListener('change', toggleRoleFields);
    } else {
        console.warn("Role select element not found on this page.");
    }
});