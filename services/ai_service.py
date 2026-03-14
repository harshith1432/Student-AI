import os
from huggingface_hub import InferenceClient

# Initialize client lazily or when HF_API_KEY is available
client = None

def get_client():
    global client
    if client is None:
        hf_key = os.environ.get("HF_API_KEY") or os.environ.get("OPENAI_API_KEY")
        
        if not hf_key or hf_key == "your_openai_api_key_here":
            return None
        # Using a reliable conversational model from HF
        client = InferenceClient("HuggingFaceH4/zephyr-7b-beta", token=hf_key)
    return client

def generate_ai_response(task_type, prompt, parameters):
    """
    Generate an AI response based on the task type, prompt, and parameters (like personality).
    Uses HuggingFace InferenceClient.
    """
    hf_client = get_client()

    personality = parameters.get('personality', 'hardworking student')
    
    system_prompts = {
        "hardworking student": "You are a hardworking, polite, and diligent student. You always say 'Yes sir/ma'am' or answer very respectfully before providing your detailed, complete assignment in markdown format.",
        "funny student": "You are a funny, slightly sarcastic but still brilliant student. You might make a small joke before providing a completely accurate and excellent assignment in markdown format.",
        "smart topper": "You are the class topper. You answer with extreme precision, advanced vocabulary, and complete confidence in your knowledge. Use proper academic formatting."
    }
    
    chosen_personality = system_prompts.get(personality, system_prompts["hardworking student"])

    task_instructions = {
        "assignment": f"Please write a high-quality academic assignment about the following topic: {prompt}. Ensure it has an introduction, body, and conclusion. Use markdown formatting with headings and bullet points where appropriate.",
        "solver": f"Please act as a solver. The teacher uploaded this question/problem: {prompt}. Provide structured answers, step-by-step explanations, and clear formatted output.",
        "notes": f"Please generate comprehensive study notes for the following chapter/topic: {prompt}. Include headings, bullet points, a summary, and key points.",
        "letter": f"Please write a letter based on this context: {prompt}. Format it as a proper formal letter with placeholders like [Date], [Recipient Name], etc., if needed."
    }

    user_content = task_instructions.get(task_type, f"Please address this prompt appropriately: {prompt}")

    if not hf_client:
        return f"### MOCK RESPONSE ({personality})\n\nAs a {personality}, I have completed the {task_type}.\n\nHere is the response for: {prompt}\n\n* Introduction\n* Body Paragraphs\n* Conclusion"

    try:
        messages = [
            {"role": "system", "content": chosen_personality},
            {"role": "user", "content": user_content}
        ]
        
        response = hf_client.chat_completion(
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content or len(content.strip()) == 0:
            # Retry once with slightly different parameters
            response = hf_client.chat_completion(
                messages=messages,
                max_tokens=2000,
                temperature=0.8
            )
            content = response.choices[0].message.content
            
        return content if content else "Sorry, I could not generate a response at this time. Please try again."
    except Exception as e:
        print(f"Error calling HuggingFace API: {e}")
        return f"Sorry, I encountered an error while trying to complete the task: {str(e)}"
