from api.bot.gpt import openai_req_generator

def create_exercise_explanation(memory: str, exercise_numbers: list) -> list:
    """
    Creates personalized explanations for why specific exercises are recommended based on user's memory
    and exercise mappings.
    
    Args:
        memory: String containing user's personal information and context
        exercise_numbers: List of exercise numbers to explain
        
    Returns:
        List of personalized explanations for each exercise
    """
    exercise_mappings = []
    
    # First collect all exercise mappings
    for exercise_num in exercise_numbers:
        try:
            with open(f'backend/api/bot/RAG/Mapping/exercise{exercise_num}.txt', 'r', encoding='utf-8') as f:
                exercise_mappings.append(f.read())
        except FileNotFoundError:
            exercise_mappings.append("Exercise mapping not found.")

    # Create one prompt for all exercises
    prompt = f"""Based on the user's personal context and the exercise suitability descriptions, explain why each exercise 
    would be beneficial for them in Persian. Keep the explanations personalized for user to get better feeling after reading them.
    
    User's context: {memory}
    
    Exercise suitability profiles:
    {"\n".join([f"Exercise {num}: {mapping}" for num, mapping in zip(exercise_numbers, exercise_mappings)])}
    
    For each exercise, provide a personalized explanation of why it is suitable for this user. 
    Format your response as a list of explanations separated by '|||'."""

    # Get all explanations in one request
    response = openai_req_generator(prompt, "")
    explanations = [exp.strip() for exp in response.split("|||")]
    
    return explanations