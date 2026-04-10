import yaml
import os

class SkillEngine:
    def __init__(self, skill_dir="skills"):
        self.skill_dir = skill_dir
        self.skills = self.load_skills()

    def load_skills(self):
        skills = []
        for file in os.listdir(self.skill_dir):
            if file.endswith(".yaml"):
                with open(os.path.join(self.skill_dir, file), "r") as f:
                    skill = yaml.safe_load(f)
                    skills.append(skill)
        return skills

    def match_skill(self, user_input):
        user_input = user_input.lower()
        for skill in self.skills:
            for trigger in skill.get("triggers", []):
                if trigger in user_input:
                    return skill
        return None