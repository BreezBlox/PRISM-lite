import requests
from config import MISTRAL_API_KEY, MISTRAL_API_URL, DEPARTMENTS

def classify_department(description):
    """Use Mistral AI to classify the department based on delay description"""
    prompt = f"""Given the following production delay description, determine which department is most likely responsible. 
    Choose from these departments: {', '.join(DEPARTMENTS)}
    
    Delay description: {description}
    
    Response format: Just return the department name, nothing else."""

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistral-tiny",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            department = response.json()['choices'][0]['message']['content'].strip()
            return department if department in DEPARTMENTS else DEPARTMENTS[0]
    except Exception as e:
        print(f"LLM classification error: {e}")
    
    return DEPARTMENTS[0]  # Default to Engineering if classification fails
