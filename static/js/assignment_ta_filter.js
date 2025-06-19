document.addEventListener('DOMContentLoaded', function() {
    const courseSelect = document.getElementById('id_course');
    const taSelect = document.getElementById('id_assigned_to');
    if (!courseSelect || !taSelect) return;

    let courseTAMap = {};
    try {
        courseTAMap = JSON.parse(taSelect.getAttribute('data-course-ta-map'));
    } catch (e) {}

    function filterTAs() {
        const selectedCourse = courseSelect.value;
        const allowedTAs = courseTAMap[selectedCourse] || [];
        Array.from(taSelect.options).forEach(option => {
            if (!option.value) return; // skip empty option
            if (allowedTAs.includes(parseInt(option.value))) {
                option.style.display = '';
            } else {
                option.style.display = 'none';
            }
        });
        // Optionally, reset selection if not valid
        if (!allowedTAs.includes(parseInt(taSelect.value))) {
            taSelect.value = '';
        }
    }

    courseSelect.addEventListener('change', filterTAs);
    filterTAs(); // Initial call
});