# 🧠 TalentScout: AI-Powered Interview Assistant

> **An intelligent chatbot built with Streamlit + Hugging Face LLMs to revolutionize technical hiring.**

---

## 🚀 Overview

**TalentScout** is your smart hiring assistant that simplifies and personalizes the **technical interview process**. Built using **Streamlit**, it interacts with candidates in a step-by-step conversational flow—collecting details, analyzing tech stack, and generating **custom technical questions** using Hugging Face’s **Zephyr-7B** model.

✅ Stores results in SQLite    
✅ Lets users **download assessment summaries**    
✅ Automatically adjusts question difficulty    
✅ Built for **HR, recruiters, and startups** alike    

---

## 🛠️ Features at a Glance

🔹 Conversational UI for candidate onboarding    
🔹 Tech stack parsing & validation    
🔹 Custom question generation (3 per tech)    
🔹 SQLite database logging    
🔹 .TXT assessment export    
🔹 Multi-step form with progress tracking    
🔹 Fully local with Hugging Face integration    

---

## 📦 Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/jbsroop/Intelligent-Hiring-Assistant-chatbot.git
cd talentscout
```

### 2. Set Up Virtual Environment (Recommended)

```bash
python -m venv venv
# For Windows
venv\Scripts\activate
# For Unix/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` should include:

```txt
streamlit==1.39.0
python-dotenv==1.0.1
huggingface_hub==0.25.1
```

### 4. Configure Environment

Create a `.env` file in the root folder:

```
HF_TOKEN=your_hugging_face_api_token
HF_MODEL=HuggingFaceH4/zephyr-7b-beta
```

> 🔐 Get your Hugging Face token from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### 5. Run the Application

```bash
streamlit run app.py
```

🖥️ Navigate to: [http://localhost:8501](http://localhost:8501)

---

## 🧑‍💻 How It Works

### 👋 Step 1: Greeting & Name

A chatbot welcomes candidates and asks for their name.

### 📇 Step 2: Candidate Info

Fill out a short form:

* Email
* Phone Number
* Role applied for
* Location
* Years of experience

### 🧠 Step 3: Technical Skills

List your known technologies (e.g., Python, Django, React).

### 🧪 Step 4: Assessment

Based on your tech stack & experience, the chatbot generates tailored technical questions.

### ✅ Step 5: Review & Submit

You can review, edit, and submit your answers.

### 📄 Step 6: Download Summary

Download the full session as a `.txt` file. Option to start a new assessment.

---

## 🧱 System Architecture

```
Streamlit UI (app.py)
    |
    |---> llm_utils.py (Zephyr-7B prompt, tech parser, retries, regex for email, phone)
    |---> db_utils.py (SQLite storage & queries)
    |
Session State ←→ Multi-step form flow
```

---

## 🤖 Prompt Engineering

The system sends structured prompts like:

```text
Generate exactly 3 technical questions about {tech} for a candidate with {years_experience} years of experience.
Difficulty level: {difficulty}
Format each question like:
1. ...
2. ...
3. ...
```

**Guidelines Enforced:**

* No yes/no questions
* Questions must vary: syntax, logic, debugging, architecture
* Difficulty auto-scaled: beginner, intermediate, advanced

---

## 🧠 Smart Error Handling

| Challenge                                | Solution                                              |
| ---------------------------------------- | ----------------------------------------------------- |
| LLM fails/empty output                   | Retry mechanism + fallback default questions          |
| Dirty tech inputs (e.g., "js", "Nodejs") | `parse_tech_stack()` with name normalizer             |
| Form crashes or progress lost            | Streamlit `session_state` preserves state             |
| Input format errors                      | Regex-based `validate_email()` and `validate_phone()` |
| Schema conflicts in DB                   | SQLite auto-checks with `CREATE TABLE IF NOT EXISTS`  |

---

## 🧩 Technologies Used

| Tool                | Purpose                       |
| ------------------- | ----------------------------- |
| **Streamlit**       | Web frontend                  |
| **Zephyr-7b-beta**  | Question generation           |
| **SQLite**          | Lightweight storage           |
| **HuggingFace Hub** | LLM API                       |
| **dotenv**          | Secure environment management |
| **re**              | Validation with regex         |

---

## 📬 Contact

For feedback, contributions, or feature requests:
**Project Maintainer**: **Jamgala Bala Swaroop**
📧 Email: [jbsroop@gmail.com](mailto:jbsroop@gmail.com)
🔗 GitHub: [https://github.com/jbsroop/Intelligent-Hiring-Assistant-chatbot.git](https://github.com/jbsroop/Intelligent-Hiring-Assistant-chatbot.git)
