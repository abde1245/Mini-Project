document.addEventListener('DOMContentLoaded', function() {
    const taSelect = document.getElementById('id_ta');
    const courseSelect = document.getElementById('id_course');
    if (!taSelect || !courseSelect) return;

    let taCoursesMap = {};
    try {
        taCoursesMap = JSON.parse(courseSelect.getAttribute('data-ta-courses'));
    } catch (e) {}

    function filterCourses() {
        const selectedTA = taSelect.value;
        const allowedCourses = taCoursesMap[selectedTA] || [];
        Array.from(courseSelect.options).forEach(option => {
            if (!option.value) return; // skip empty option
            if (allowedCourses.includes(parseInt(option.value))) {
                option.style.display = '';
            } else {
                option.style.display = 'none';
            }
        });
        // Optionally, reset selection if not valid
        if (!allowedCourses.includes(parseInt(courseSelect.value))) {
            courseSelect.value = '';
        }
    }

    taSelect.addEventListener('change', filterCourses);
    filterCourses(); // Initial call
});