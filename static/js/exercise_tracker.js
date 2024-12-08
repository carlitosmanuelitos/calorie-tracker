document.addEventListener('DOMContentLoaded', () => {
    const addExerciseBtn = document.getElementById('add-exercise-btn');
    const exerciseModal = document.getElementById('exercise-modal');
    const closeModalBtn = document.getElementById('close-modal');
    const exerciseForm = document.getElementById('exercise-form');
    const exerciseLogBody = document.getElementById('exercise-log-body');

    // Modal toggle functions
    addExerciseBtn.addEventListener('click', () => {
        exerciseModal.classList.remove('hidden');
    });

    closeModalBtn.addEventListener('click', () => {
        exerciseModal.classList.add('hidden');
    });

    // Form submission handler
    exerciseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(exerciseForm);
        const exerciseData = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/exercise-log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrf_token')
                },
                body: JSON.stringify(exerciseData)
            });

            if (!response.ok) {
                throw new Error('Failed to log exercise');
            }

            const newExercise = await response.json();
            addExerciseToTable(newExercise);
            
            // Reset and close modal
            exerciseForm.reset();
            exerciseModal.classList.add('hidden');
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to log exercise. Please try again.');
        }
    });

    // Function to add exercise to table
    function addExerciseToTable(exercise) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="py-3 px-6">${new Date(exercise.date).toLocaleDateString()}</td>
            <td class="py-3 px-6">${exercise.exercise_type}</td>
            <td class="py-3 px-6">${exercise.duration} mins</td>
            <td class="py-3 px-6">${exercise.intensity}</td>
            <td class="py-3 px-6">
                <button class="text-blue-500 hover:text-blue-700">Edit</button>
                <button class="text-red-500 hover:text-red-700">Delete</button>
            </td>
        `;
        exerciseLogBody.prepend(row);
    }

    // Fetch existing exercise logs on page load
    async function fetchExerciseLogs() {
        try {
            const response = await fetch('/api/exercise-logs');
            if (!response.ok) {
                throw new Error('Failed to fetch exercise logs');
            }
            const exercises = await response.json();
            exercises.forEach(addExerciseToTable);
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Utility function to get CSRF token
    function getCookie(name) {
        const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)')?.pop() || '';
        return cookieValue;
    }

    // Initial load of exercise logs
    fetchExerciseLogs();
});
