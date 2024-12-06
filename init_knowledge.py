from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.knowledge import KnowledgeCategory

def init_knowledge_base():
    db = SessionLocal()
    
    categories = [
        {
            "title": "Weight Loss",
            "description": "Evidence-based strategies and tips for healthy, sustainable weight loss",
            "content": """
                <h2 class="text-2xl font-bold mb-4">Weight Loss Fundamentals</h2>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Caloric Deficit</h3>
                <p class="mb-4">The fundamental principle of weight loss is maintaining a caloric deficit. This means consuming fewer calories than your body burns. A safe and sustainable deficit is typically 500-750 calories below maintenance.</p>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Sustainable Rate of Loss</h3>
                <p class="mb-4">Aim for 0.5-1kg (1-2 lbs) per week. This rate helps preserve muscle mass and is more sustainable long-term.</p>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Nutrition Guidelines</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Prioritize protein (1.6-2.2g per kg of body weight)</li>
                    <li>Include plenty of fiber-rich vegetables</li>
                    <li>Stay hydrated (minimum 2-3 liters daily)</li>
                    <li>Limit processed foods and added sugars</li>
                </ul>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Exercise Recommendations</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Combine resistance training and cardio</li>
                    <li>Aim for 150+ minutes of moderate activity weekly</li>
                    <li>Include strength training 2-3 times per week</li>
                    <li>Focus on consistency over intensity</li>
                </ul>
            """
        },
        {
            "title": "Muscle Gain/Bulking",
            "description": "Guidelines for building muscle mass effectively and safely",
            "content": """
                <h2 class="text-2xl font-bold mb-4">Muscle Building Essentials</h2>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Caloric Surplus</h3>
                <p class="mb-4">To build muscle, you need to eat more calories than your body burns. Aim for a surplus of 300-500 calories above maintenance for lean gaining.</p>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Protein Requirements</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>1.6-2.2g protein per kg of body weight</li>
                    <li>Spread protein intake across 4-6 meals</li>
                    <li>Include complete protein sources</li>
                </ul>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Training Principles</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Progressive overload is key</li>
                    <li>Focus on compound movements</li>
                    <li>Train each muscle group 2-3 times per week</li>
                    <li>Allow adequate recovery between sessions</li>
                </ul>
            """
        },
        {
            "title": "General Health & Wellness",
            "description": "Comprehensive approach to maintaining overall health and wellness",
            "content": """
                <h2 class="text-2xl font-bold mb-4">Health & Wellness Foundations</h2>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Balanced Nutrition</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Eat a variety of whole foods</li>
                    <li>Include all macronutrients</li>
                    <li>Focus on nutrient-dense foods</li>
                    <li>Practice portion control</li>
                </ul>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Sleep Optimization</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Aim for 7-9 hours per night</li>
                    <li>Maintain consistent sleep schedule</li>
                    <li>Create a relaxing bedtime routine</li>
                </ul>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Stress Management</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Practice regular meditation or mindfulness</li>
                    <li>Engage in regular physical activity</li>
                    <li>Maintain work-life balance</li>
                </ul>
            """
        },
        {
            "title": "Athletic Performance",
            "description": "Tips and strategies for improving sports and athletic performance",
            "content": """
                <h2 class="text-2xl font-bold mb-4">Athletic Performance Enhancement</h2>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Training Periodization</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Plan training cycles strategically</li>
                    <li>Include both intensity and volume</li>
                    <li>Allow for proper deload periods</li>
                </ul>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Performance Nutrition</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Time nutrients around workouts</li>
                    <li>Optimize pre/post workout meals</li>
                    <li>Stay hydrated during activity</li>
                </ul>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Recovery Strategies</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Utilize active recovery methods</li>
                    <li>Implement proper cool-down routines</li>
                    <li>Consider recovery modalities (massage, etc.)</li>
                </ul>
            """
        },
        {
            "title": "Rehabilitation",
            "description": "Guidelines for safe recovery and return to activity after injury",
            "content": """
                <h2 class="text-2xl font-bold mb-4">Rehabilitation Principles</h2>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Recovery Phases</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Acute phase management</li>
                    <li>Progressive mobility work</li>
                    <li>Strength restoration</li>
                    <li>Return to activity protocol</li>
                </ul>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Nutrition for Healing</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Adequate protein intake</li>
                    <li>Anti-inflammatory foods</li>
                    <li>Micronutrient considerations</li>
                </ul>
                
                <h3 class="text-xl font-semibold mt-6 mb-3">Exercise Progression</h3>
                <ul class="list-disc pl-6 mb-4">
                    <li>Start with basic movements</li>
                    <li>Gradually increase intensity</li>
                    <li>Monitor pain and symptoms</li>
                    <li>Work with healthcare providers</li>
                </ul>
            """
        }
    ]
    
    # Add categories to database
    for category_data in categories:
        category = KnowledgeCategory(**category_data)
        db.add(category)
    
    db.commit()
    db.close()

if __name__ == "__main__":
    init_knowledge_base()
