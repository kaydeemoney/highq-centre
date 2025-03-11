const filterDropdown = document.getElementById('filter');
const courseSection = document.getElementById('course-section');
const studentSection = document.getElementById('student-section');
const studentNameInput = document.getElementById('student-name');
const studentList = document.getElementById('student-list');

// Fetch JSON data for dynamic filtering
fetch('/static/data.json')
    .then(response => response.json())
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

// Show/hide sections based on filter selection
filterDropdown.addEventListener('change', (e) => {
    const value = e.target.value;
    courseSection.style.display = value === 'course' ? 'block' : 'none';
    studentSection.style.display = value === 'student' ? 'block' : 'none';
});

function addConceptField() {
    const container = document.getElementById('concepts');
    const div = document.createElement('div');
    div.className = 'concept-item';
    div.innerHTML = `
        <textarea name="concepts[]" rows="2" required></textarea>
        <input type="url" name="concept_links[]" placeholder="Link for this concept">
    `;
    container.insertBefore(div, container.lastElementChild);
}

function addResourceField() {
    const container = document.getElementById('resources');
    const div = document.createElement('div');
    div.className = 'resource-item';
    div.innerHTML = `
        <textarea name="resources[]" rows="2" required></textarea>
        <input type="url" name="resource_links[]" placeholder="Link for this resource">
    `;
    container.insertBefore(div, container.lastElementChild);
}


document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("performanceChart").getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6", "Week 7", "Week 8", "Week 9", "Week 10"],
            datasets: [
                {
                    label: "Performance (%)",
                    data: [85, 90, 78, 92, 88, 76, 95, 89, 91, 94],
                    borderColor: "#3498db",
                    backgroundColor: "rgba(52, 152, 219, 0.2)",
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
});
