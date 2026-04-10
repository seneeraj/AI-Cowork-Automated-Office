from services.llm import generate_response

class Executor:
    def run_steps(self, steps, user_input=None):
        results = []

        for step in steps:
            result = self.execute_step(step, user_input)
            results.append(result)

        return results

    def execute_step(self, step, context):
        step_lower = step.lower()

        # -----------------------------
        # Example Automation Hooks
        # -----------------------------
        if "send email" in step_lower:
            from integrations.gmail import send_email
            return send_email("test@example.com", "Subject", "Generated content")

        if "save data" in step_lower:
            from integrations.sheets import save_to_sheet
            return save_to_sheet({"data": context})

        # -----------------------------
        # Default AI Execution
        # -----------------------------
        prompt = f"""
Execute this workflow step clearly.

Step:
{step}

Context:
{context}

IMPORTANT:
- Do NOT include Summary/Recommendation
- Only return the result of THIS step
- Keep output short and clear
"""
        return generate_response(prompt)