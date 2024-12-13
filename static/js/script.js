const filterDropdown = document.getElementById('filter');
const courseSection = document.getElementById('course-section');
const studentSection = document.getElementById('student-section');
const studentNameInput = document.getElementById('student-name');
const studentList = document.getElementById('student-list');

// Dummy student names
const students = ['Frank', 'Francis', 'Francesca', 'Freddie', 'George', 'Geraldine', 'Gloria'];

// Show and hide sections based on filter selection
filterDropdown.addEventListener('change', (e) => {
    const value = e.target.value;
    if (value === 'course') {
      courseSection.style.display = 'block';
      studentSection.style.display = 'none';
    } else if (value === 'student') {
      courseSection.style.display = 'none';
      studentSection.style.display = 'block';
      studentNameInput.style.display = 'block'; // Ensure the input box is shown
    } else {
      courseSection.style.display = 'none';
      studentSection.style.display = 'none';
      studentNameInput.style.display = 'none'; // Hide the input box if no filter is selected
    }
  });
  

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
