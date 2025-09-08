# Mini AI Symptom Checker with 100 symptoms

# Get user input
question = input("What's your symptom(s)? ").lower()

# Dictionary of symptoms and advice (example list, expand to 100)
advice_dict = {
    "fever": "You might need rest, hydration, and monitor your temperature.",
    "headache": "Try relaxing, resting, or taking mild pain relief.",
    "cough": "Drink warm fluids and consider a cough syrup if persistent.",
    "sore throat": "Gargle warm salt water and stay hydrated.",
    "fatigue": "Rest well, eat nutritious food, and avoid overexertion.",
    "nausea": "Eat light meals and stay hydrated.",
    "vomiting": "Drink fluids slowly and rest.",
    "diarrhea": "Stay hydrated and avoid heavy foods.",
    "dizziness": "Sit or lie down and avoid sudden movements.",
    "muscle pain": "Rest, gentle stretching, and consider pain relief.",
    "back pain": "Use heat or cold packs and gentle movement.",
    "runny nose": "Stay hydrated and consider saline nasal spray.",
    "chills": "Keep warm and rest.",
    "sneezing": "Check for allergies and rest.",
    "shortness of breath": "Seek medical attention if severe.",
    "chest pain": "Seek immediate medical attention.",
    "rash": "Avoid scratching and apply soothing lotion.",
    "joint pain": "Rest, gentle movement, and consider anti-inflammatory meds.",
    "anxiety": "Try deep breathing and relaxation techniques.",
    "depression": "Seek support and talk to a mental health professional.",
    # ... continue until you reach 100 symptoms
}

# Check for symptoms in input
found = False
for symptom, advice in advice_dict.items():
    if symptom in question:
        print(f"Advice for {symptom}: {advice}")
        found = True

if not found:
    print("Sorry, I don't have advice for that symptom.")
