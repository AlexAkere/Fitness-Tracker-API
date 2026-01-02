const API_URL = "http://127.0.0.1:8000/workouts";
let currentEditingId = null; // Stores the ID of the workout we are editing

// 1. Fetch and Display Workouts
async function fetchWorkouts() {
    const response = await fetch(API_URL);
    const workouts = await response.json();
    const list = document.getElementById("workout-list");
    list.innerHTML = ""; 

    workouts.forEach(workout => {
        const div = document.createElement("div");
        div.className = "workout-card";
        div.innerHTML = `
            <div class="workout-info">
                <strong>${workout.exercise}</strong>
                <span class="workout-stats">🔥 ${workout.weight} lbs  ×  ${workout.reps} reps</span>
            </div>
            <div>
                <button onclick="startEdit(${workout.id}, '${workout.exercise}', ${workout.weight}, ${workout.reps})" class="edit-btn">Edit</button>
                <button onclick="deleteWorkout(${workout.id})" class="delete-btn">Delete</button>
            </div>
        `;
        list.appendChild(div);
    });
}

// 2. Handle Form Submit (Create OR Update)
document.getElementById("workout-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const exercise = document.getElementById("exercise").value;
    const weight = document.getElementById("weight").value;
    const reps = document.getElementById("reps").value;
    const btn = document.getElementById("add-btn");

    if (currentEditingId) {
        // --- UPDATE MODE (PUT) ---
        await fetch(`${API_URL}/${currentEditingId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ exercise, weight, reps })
        });
        
        // Reset everything back to normal
        currentEditingId = null;
        btn.innerHTML = "<span>+</span> Log Workout";
        btn.style.background = "#00e676"; // Back to Green
    } else {
        // --- CREATE MODE (POST) ---
        await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ exercise, weight, reps })
        });
    }

    document.getElementById("workout-form").reset();
    fetchWorkouts();
});

// 3. Start Editing (Fill the form)
function startEdit(id, exercise, weight, reps) {
    currentEditingId = id;
    
    // Fill the inputs with existing data
    document.getElementById("exercise").value = exercise;
    document.getElementById("weight").value = weight;
    document.getElementById("reps").value = reps;

    // Change the button look
    const btn = document.getElementById("add-btn");
    btn.innerHTML = "<span>💾</span> Update Workout";
    btn.style.background = "#29b6f6"; // Turn Blue
}

// 4. Delete Workout
async function deleteWorkout(id) {
    if(confirm("Are you sure you want to delete this log?")) {
        await fetch(`${API_URL}/${id}`, { method: "DELETE" });
        fetchWorkouts();
    }
}

// Initial Load
fetchWorkouts();