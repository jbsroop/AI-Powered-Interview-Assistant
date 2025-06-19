import os
from huggingface_hub import InferenceClient
import re
from typing import List
import logging

# Set up logging
logging.basicConfig(filename="llm_errors.log", level=logging.ERROR)

class LLMHelper:
    def __init__(self):
        self.client = InferenceClient(
            model="HuggingFaceH4/zephyr-7b-beta",
            token="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"
        )
        
    def generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text from the LLM with error handling and retry"""
        for attempt in range(2):  # Retry once on failure
            try:
                response = self.client.text_generation(
                    prompt,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True
                )
                return response.strip()
            except Exception as e:
                logging.error(f"LLM Error (Attempt {attempt + 1}): {str(e)}")
                if attempt == 1:
                    return ""
        return ""

def parse_tech_stack(input_str: str) -> List[str]:
    """Parse tech stack input into a cleaned list of technologies"""
    if not input_str.strip():
        return []
    
    replacements = {
        "c#": "C#",
        "c++": "C++",
        "f#": "F#",
        "golang": "Go",
        "js": "JavaScript",
        "ts": "TypeScript",
        "nodejs": "Node.js",
        "node": "Node.js",
        "reactjs": "React",
        "vuejs": "Vue.js",
        "postgresql": "PostgreSQL",
        "mysql": "MySQL"
    }
    
    techs = re.split(r'[,;/\n]', input_str)
    cleaned = []
    
    for tech in techs:
        tech = tech.strip()
        if tech:
            tech = tech.lower()
            tech = replacements.get(tech, tech)
            if not re.match(r'^[a-z0-9+#]+$', tech):
                tech = tech.title()
            if tech not in cleaned and len(tech) > 1:
                cleaned.append(tech)
    
    return cleaned

def generate_tech_questions(tech_stack: List[str], years_experience: int) -> List[str]:
    """Generate technical questions based on tech stack and experience level"""
    if not tech_stack:
        return ["Please describe your technical experience."]

    llm = LLMHelper()
    difficulty = "beginner" if years_experience < 2 else "intermediate" if years_experience < 5 else "advanced"
    questions = []
    
    for tech in tech_stack:
        prompt = f"""Generate exactly 3 technical questions about {tech} for a candidate with {years_experience} years of experience.
Difficulty level: {difficulty}
Format each question clearly numbered like:
1. [Question about {tech}]
2. [Question about {tech}] 
3. [Question about {tech}]

The questions should:
- Be technical and specific to {tech}
- Cover different aspects (syntax, architecture, debugging)
- Require detailed answers
- Avoid simple yes/no or one-word answers
- Be unique and not repetitive
- Be relevant to real-world use cases

Example for Python (intermediate):
1. How would you optimize memory usage in a Python application processing large datasets?
2. Explain the differences between multiprocessing and threading in Python with examples.
3. Describe how you would implement and test a custom context manager in Python.
"""
        response = llm.generate_text(prompt)
        
        tech_questions = []
        for line in response.split('\n'):
            line = line.strip()
            if line and re.match(r'^\d+\.\s*\[.*\]\s*$', line):
                question = line.split('.', 1)[1].strip()[1:-1].strip()
                if question:
                    tech_questions.append(f"{tech}: {question}")
        
        if len(tech_questions) < 3:
            default_questions = [
                f"{tech}: Explain the most challenging {tech} project you've worked on and the key technical decisions you made.",
                f"{tech}: How would you optimize performance in a {tech} application handling high traffic?",
                f"{tech}: Describe your approach to debugging a complex issue in a {tech} application."
            ]
            tech_questions.extend(default_questions[:3 - len(tech_questions)])
        
        questions.extend(tech_questions[:3])
    
    return questions[:15]  # Limit to 15 questions max to avoid overwhelming candidates