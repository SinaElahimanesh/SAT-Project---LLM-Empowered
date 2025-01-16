import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
import glob
import re

model = SentenceTransformer('sentence-transformers/LaBSE')

def retrieve_relevant_exercise(query: str, done_exercises: List[int] = None) -> List[Tuple[int, float]]:
    if done_exercises is None:
        done_exercises = []
        
    # Encode the query
    query_embedding = model.encode([query])
    
    # Get all exercise files
    exercise_files = glob.glob('backend/api/bot/RAG/Mapping/exercise*.txt')
    
    # Store exercise contents and their embeddings
    exercise_contents = []
    exercise_embeddings = []
    exercise_numbers = []
    
    # Read and encode each exercise
    for file_path in exercise_files:
        # Extract exercise number from filename
        match = re.search(r'exercise(\d+)\.txt$', file_path)
        if match:
            exercise_num = int(match.group(1))
            if exercise_num not in done_exercises:  # Skip if exercise is already done
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    exercise_contents.append((file_path, content))
                    exercise_embeddings.append(model.encode([content])[0])
                    exercise_numbers.append(exercise_num)
    
    if not exercise_embeddings:  # If all exercises are done
        return []
        
    # Convert list of embeddings to numpy array
    exercise_embeddings = np.array(exercise_embeddings)
    
    # Calculate cosine similarities
    similarities = cosine_similarity(query_embedding, exercise_embeddings)[0]
    
    # Get indices of top 5 similar exercises
    top_5_indices = np.argsort(similarities)[-5:][::-1]
    
    # Create list of (exercise_number, similarity_score) tuples
    results = []
    for idx in top_5_indices:
        similarity_score = similarities[idx]
        exercise_num = exercise_numbers[idx]
        results.append((exercise_num, float(similarity_score)))
    
    return results


def get_exercise_content(exercise_tuples: List[Tuple[int, float]]) -> List[str]:
    """
    Get the content of exercises from their numbers and similarity scores.
    
    Args:
        exercise_tuples: List of tuples containing (exercise_number, similarity_score)
        
    Returns:
        List of exercise contents as strings
    """
    exercise_contents = []
    
    for exercise_num, _ in exercise_tuples:
        file_path = f'backend/api/bot/RAG/Exercises/exercise{exercise_num}.txt'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                exercise_contents.append(content)
        except FileNotFoundError:
            print(f"Exercise file {file_path} not found")
            continue
            
    return exercise_contents
