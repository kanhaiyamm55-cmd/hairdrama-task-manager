
import os
from functools import wraps

from flask import Blueprint, request, jsonify, g
from supabase import create_client

from app.services.email_service import send_email

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


# Supabase connection
def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise RuntimeError("Supabase environment variables are missing")

    return create_client(url, key)


# Authentication middleware
def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication token required"}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            client = get_supabase()
            response = client.auth.get_user(token)
            g.user = response.user

            if not g.user:
                return jsonify({"error": "Invalid authentication token"}), 401

        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 401

        return func(*args, **kwargs)

    return wrapper


# Save or update user profile
def save_user_profile(client, user):
    metadata = user.user_metadata or {}

    client.table("profiles").upsert({
        "id": str(user.id),
        "email": user.email,
        "full_name": (
            metadata.get("full_name")
            or metadata.get("name")
            or user.email
        ),
        "avatar_url": (
            metadata.get("avatar_url")
            or metadata.get("picture")
        )
    }).execute()


# Get a profile by user ID
def get_profile(client, user_id):
    result = (
        client.table("profiles")
        .select("id, full_name, email")
        .eq("id", user_id)
        .execute()
    )

    return result.data[0] if result.data else None


# GET tasks created by user OR assigned to user
@tasks_bp.get("")
@require_auth
def get_tasks():
    try:
        client = get_supabase()
        user_id = str(g.user.id)

        created_result = (
            client.table("tasks")
            .select("*")
            .eq("created_by", user_id)
            .execute()
        )

        created_tasks = created_result.data or []

        assignment_result = (
            client.table("task_assignments")
            .select("task_id")
            .eq("user_id", user_id)
            .execute()
        )

        assigned_task_ids = list({
            item["task_id"]
            for item in (assignment_result.data or [])
        })

        assigned_tasks = []

        if assigned_task_ids:
            assigned_result = (
                client.table("tasks")
                .select("*")
                .in_("id", assigned_task_ids)
                .execute()
            )
            assigned_tasks = assigned_result.data or []

        all_tasks = {}

        for task in created_tasks + assigned_tasks:
            all_tasks[str(task["id"])] = task

        tasks = list(all_tasks.values())

        tasks.sort(
            key=lambda task: task.get("created_at") or "",
            reverse=True
        )

        return jsonify({"tasks": tasks}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# CREATE a new task
@tasks_bp.post("")
@require_auth
def create_task():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if len(title) > 160:
        return jsonify({
            "error": "Title must be 160 characters or less"
        }), 400

    priority = data.get("priority", "medium")

    if priority not in ["low", "medium", "high"]:
        return jsonify({"error": "Invalid priority"}), 400

    try:
        client = get_supabase()
        user_id = str(g.user.id)

        save_user_profile(client, g.user)

        task_data = {
            "title": title,
            "description": data.get("description", ""),
            "priority": priority,
            "created_by": user_id
        }

        if data.get("due_date"):
            task_data["due_date"] = data["due_date"]

        result = (
            client.table("tasks")
            .insert(task_data)
            .execute()
        )

        return jsonify({
            "message": "Task created successfully",
            "task": result.data[0]
        }), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# UPDATE task status
@tasks_bp.patch("/<task_id>")
@require_auth
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    allowed_statuses = [
        "pending",
        "in_progress",
        "completed"
    ]

    if status not in allowed_statuses:
        return jsonify({"error": "Invalid task status"}), 400

    try:
        client = get_supabase()
        user_id = str(g.user.id)

        # Fetch task details before updating
        task_result = (
            client.table("tasks")
            .select("*")
            .eq("id", task_id)
            .execute()
        )

        if not task_result.data:
            return jsonify({"error": "Task not found"}), 404

        existing_task = task_result.data[0]
        creator_id = str(existing_task["created_by"])

        # Check creator permission
        is_creator = creator_id == user_id

        # Check assigned-user permission
        is_assigned_user = False

        if not is_creator:
            assignment = (
                client.table("task_assignments")
                .select("task_id")
                .eq("task_id", task_id)
                .eq("user_id", user_id)
                .execute()
            )

            is_assigned_user = bool(assignment.data)

        if not is_creator and not is_assigned_user:
            return jsonify({
                "error": "You are not authorized to update this task"
            }), 403

        old_status = existing_task.get("status")

        result = (
            client.table("tasks")
            .update({"status": status})
            .eq("id", task_id)
            .execute()
        )

        if not result.data:
            return jsonify({"error": "Task status update failed"}), 500

        # Send email only when task changes to completed
        if (
            status == "completed"
            and old_status != "completed"
            and not is_creator
        ):
            try:
                creator = get_profile(client, creator_id)

                if creator and creator.get("email"):
                    task_title = existing_task.get("title", "Task")

                    send_email(
                        creator["email"],
                        f"Task completed: {task_title}",
                        (
                            f"Hello {creator.get('full_name') or 'User'},\n\n"
                            f"The task assigned by you has been completed.\n\n"
                            f"Task: {task_title}\n"
                            f"Status: Completed\n\n"
                            "Hairdrama Task Manager"
                        )
                    )

            except Exception as email_error:
                print(f"Completion email error: {email_error}")

        return jsonify({
            "message": "Task status updated successfully",
            "task": result.data[0]
        }), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# GET registered team members
@tasks_bp.get("/users")
@require_auth
def get_users():
    try:
        client = get_supabase()
        user_id = str(g.user.id)

        result = (
            client.table("profiles")
            .select("id, full_name, email")
            .neq("id", user_id)
            .order("full_name")
            .execute()
        )

        return jsonify({"users": result.data or []}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


# ASSIGN task to another registered user
@tasks_bp.post("/<task_id>/assign")
@require_auth
def assign_task(task_id):
    data = request.get_json(silent=True) or {}
    assigned_user_id = data.get("user_id")

    if not assigned_user_id:
        return jsonify({"error": "User ID is required"}), 400

    try:
        client = get_supabase()
        current_user_id = str(g.user.id)

        # Verify task belongs to current user
        task_result = (
            client.table("tasks")
            .select("*")
            .eq("id", task_id)
            .eq("created_by", current_user_id)
            .execute()
        )

        if not task_result.data:
            return jsonify({
                "error": "Task not found or not authorized"
            }), 404

        task = task_result.data[0]

        # Verify assigned user exists
        assigned_user = get_profile(client, assigned_user_id)

        if not assigned_user:
            return jsonify({
                "error": "Assigned user not found"
            }), 404

        # Save assignment
        result = (
            client.table("task_assignments")
            .upsert({
                "task_id": task_id,
                "user_id": assigned_user_id,
                "assigned_by": current_user_id
            })
            .execute()
        )

        # Send assignment notification
        try:
            if assigned_user.get("email"):
                task_title = task.get("title", "Task")

                send_email(
                    assigned_user["email"],
                    f"New task assigned: {task_title}",
                    (
                        f"Hello {assigned_user.get('full_name') or 'User'},\n\n"
                        "A new task has been assigned to you.\n\n"
                        f"Task: {task_title}\n"
                        f"Description: {task.get('description') or 'No description'}\n"
                        f"Priority: {task.get('priority', 'medium')}\n\n"
                        "Please log in to Hairdrama Task Manager to view it."
                    )
                )

        except Exception as email_error:
            print(f"Assignment email error: {email_error}")

        return jsonify({
            "message": "Task assigned successfully",
            "assignment": result.data
        }), 201

    except Exception as error:
        return jsonify({"error": str(error)}), 500
