def get_llm_answer(question, context, api_key):
    # Validate input parameters
    if not api_key:
        raise ValueError("API key is required")
    if not question:
        raise ValueError("Question is required")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": question + context
            }
        ],
        "max_tokens": 300
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        
        # Extract the plain text answer from the response
        answer = response.json()['choices'][0]['message']['content'].strip()
        return answer
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
