import {useState} from "react"
import {useOrganization} from "@clerk/clerk-react"
import TaskColumn from "./TaskColumn"
import {createTask, updateTask, deleteTask} from "../services/api"
import TaskForm from "./TaskForm.jsx";

const STATUSES = ["pending", "started", "completed"]

function KanbanBoard({tasks, setTasks, getToken}) {
    const {membership} = useOrganization()
    const [showForm, setShowForm] = useState(false)
    const [editingTask, setEditingTask] = useState(null)

    const role = membership?.role
    const canManage = role === "org:admin" || role === "org:editor"

    function getTasksByStatus(status) {
        return tasks.filter(task => task.status === status)
    }

    function handleEdit(task) {
        setEditingTask(task)
        setShowForm(true)
    }

    async function handleDelete(taskId) {
        if (!confirm("Are you sure you want to delete this task?")) return

        const taskToDelete = tasks.find(t => t.id === taskId)
        setTasks(prev => prev.filter(t => t.id !== taskId))

        try {
            await deleteTask(getToken, taskId)
        } catch (err) {
            setTasks(prev => [...prev, taskToDelete])
            console.error(err)
        }
    }

    async function handleSubmit(taskData) {
        if (editingTask) {
            const updatedTask = {...editingTask, ...taskData}
            setTasks(prev => prev.map(t => t.id === editingTask.id ? updatedTask : t))
            setShowForm(false)
            setEditingTask(null)

            try {
                await updateTask(getToken, editingTask.id, taskData)
            } catch (err) {
                setTasks(prev => prev.map(t => t.id === editingTask.id ? editingTask : t))
                console.error(err)
            }
        } else {
            try {
                const newTask = await createTask(getToken, taskData)
                setTasks(prev => [...prev, newTask])
                setShowForm(false)
            } catch (err) {
                console.error(err)
            }
        }
    }

    function handleCancel() {
        setShowForm(false)
        setEditingTask(null)
    }

    function handleAddTask() {
        setEditingTask(null)
        setShowForm(true)
    }

    return <div className={"kanban-wrapper"}>
        <div className={"kanban-header"}>
            <h2 className={"kanban-title"}>Tasks</h2>
            {canManage && (
                <button className={"btn btn-primary"} onClick={handleAddTask}>
                    + Add Task
                </button>
            )}
        </div>

        <div className={"kanban-board"}>
            {STATUSES.map(status => (
                <TaskColumn
                    key={status}
                    status={status}
                    tasks={getTasksByStatus(status)}
                    onEdit={canManage ? handleEdit : null}
                    onDelete={canManage ? handleDelete : null}
                />
            ))}
        </div>

        {showForm && <TaskForm
            task={editingTask}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
        />}
    </div>
}

export default KanbanBoard