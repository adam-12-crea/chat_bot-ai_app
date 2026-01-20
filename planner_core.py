import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Use the reliable Flash model
model = genai.GenerativeModel('gemma-3-1b-it')

def generate_study_plan(days, subjects, goal, user_files):
    """
    Generates a text-based study plan (Markdown) compatible with the frontend.
    """
    if not api_key:
        return "⚠️ Erreur: Clé API Google manquante."

    # Format the list of files for the AI
    files_context = ", ".join(user_files) if user_files else "Aucun fichier spécifique téléversé."
    subjects_str = ", ".join(subjects)

    prompt = f"""
    Agis en tant qu'expert en planification académique.
    Crée un plan de révision pour un étudiant universitaire.
    
    **CONTEXTE:**
    - Durée: {days} jours.
    - Matières à réviser: {subjects_str}.
    - Objectif principal: {goal}.
    - Ressources disponibles (PDFs de l'étudiant): [{files_context}].
    
    **INSTRUCTIONS:**
    1. Crée un emploi du temps jour par jour.
    2. Sois précis (ex: "Jour 1: 09h00 - 11h00 : Titre du chapitre").
    3. IMPORTANT: Si une matière correspond à un des fichiers PDF listés ci-dessus, dis explicitement à l'étudiant de lire ce fichier.
    4. Utilise un format clair et lisible (Markdown).
    5. Inclus des pauses.

    **FORMAT DE RÉPONSE ATTENDU (Markdown):**
    
    ### Jour 1 : [Thème]
    * **09:00 - 11:00 :** [Matière] - [Sujet précis]
        * *Ressource recommandée :* [Nom du fichier PDF si applicable, sinon "Cours général"]
    * **11:00 - 11:15 :** Pause
    ...
    """

    try:
        response = model.generate_content(prompt)
        # Return the raw text so the frontend can display it properly
        return response.text
    except Exception as e:
        print(f"❌ Planner Error: {e}")
        return "Désolé, une erreur est survenue lors de la génération du planning. Veuillez réessayer."