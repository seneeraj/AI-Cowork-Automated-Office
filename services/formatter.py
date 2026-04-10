def format_task_output(skill_name, results):
    return {
        "Summary": f"Executed {skill_name}",
        "Steps": results,
        "Status": "Completed"
    }