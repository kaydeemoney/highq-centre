const filterDropdown = document.getElementById('filter');
const courseSection = document.getElementById('course-section');
const studentSection = document.getElementById('student-section');
const studentNameInput = document.getElementById('student-name');
const studentList = document.getElementById('student-list');

// Fetch JSON data
fetch('static/data.json')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json(); // Parse the JSON data
    })
    .then(data => {
        const students = data;

        // Filter student names dynamically
        studentNameInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            studentList.innerHTML = '';

            const filteredStudents = students.filter(student =>
                student.toLowerCase().startsWith(query)
            );

            filteredStudents.forEach(student => {
                const li = document.createElement('li');
                li.textContent = student;
                li.addEventListener('click', () => {
                    studentNameInput.value = student;
                    studentList.innerHTML = '';
                });
                studentList.appendChild(li);
            });
        });
    })
    .catch(error => {
        console.error('Error loading JSON data:', error);
    });

// Show and hide sections based on filter selection
filterDropdown.addEventListener('change', (e) => {
    const value = e.target.value;
    if (value === 'course') {
        courseSection.style.display = 'block';
        studentSection.style.display = 'none';
    } else if (value === 'student') {
        courseSection.style.display = 'none';
        studentSection.style.display = 'block';
        studentNameInput.style.display = 'block';
    } else {
        courseSection.style.display = 'none';
        studentSection.style.display = 'none';
        studentNameInput.style.display = 'none';
    }
});
