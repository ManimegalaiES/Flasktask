const taskForm = document.getElementById("taskForm");
const taskTitle = document.getElementById("taskTitle");
const taskList = document.getElementById("taskList");
const message = document.getElementById("message");
const addButton = document.getElementById("addButton");

taskForm.addEventListener("submit", async function (event) {
    
    event.preventDefault();

    const title = taskTitle.value.trim();

    if (!title) {
        showMessage("Please enter a task title!", false);
        return;
    }

    addButton.disabled = true;
    message.textContent = "Adding task...";
    message.className = "";

    try {
        const response = await fetch("/add_task", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: title
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.message || "Could not add task.", false);
            return;
        }

        const emptyMessage = document.getElementById("emptyMessage");

        if (emptyMessage) {
            emptyMessage.remove();
        }

        const li = document.createElement("li");
        li.className = "task-item";

        const titleSpan = document.createElement("span");
        titleSpan.className = "task-title";
        titleSpan.textContent = data.task.title;

        const statusSpan = document.createElement("span");
        statusSpan.className = "status";
        statusSpan.textContent = data.task.status;

        li.appendChild(titleSpan);
        li.appendChild(statusSpan);

        taskList.prepend(li);

        taskTitle.value = "";

        showMessage(data.message, true);

    } catch (error) {
        showMessage("Unable to connect to the server.", false);
    } finally {
        addButton.disabled = false;
    }
});

function showMessage(text, success) {
    message.textContent = text;
    message.className = success ? "success" : "error-message";
}