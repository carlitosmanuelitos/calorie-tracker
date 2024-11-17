// Constants for calculations
const ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'lightly_active': 1.375,
    'moderately_active': 1.55,
    'very_active': 1.725,
    'extremely_active': 1.9
};

const MACRO_RATIOS = {
    'weight_loss': {
        protein: 0.40,    // 40% protein
        fat: 0.35,        // 35% fat
        carbs: 0.25       // 25% carbs
    },
    'muscle_gain': {
        protein: 0.30,    // 30% protein
        fat: 0.20,        // 20% fat
        carbs: 0.50       // 50% carbs
    },
    'maintenance': {
        protein: 0.30,    // 30% protein
        fat: 0.30,        // 30% fat
        carbs: 0.40       // 40% carbs
    },
    'general_fitness': {
        protein: 0.25,    // 25% protein
        fat: 0.25,        // 25% fat
        carbs: 0.50       // 50% carbs
    },
    'athletic_performance': {
        protein: 0.30,    // 30% protein
        fat: 0.20,        // 20% fat
        carbs: 0.50       // 50% carbs
    }
};

// Calculate BMI
function calculateBMI(weight, height) {
    const heightInMeters = height / 100;
    const bmi = weight / (heightInMeters * heightInMeters);
    return Math.round(bmi * 10) / 10;
}

// Calculate TDEE (Total Daily Energy Expenditure)
function calculateTDEE(weight, height, age, gender, activityLevel) {
    // Calculate BMR using Mifflin-St Jeor Equation
    let bmr;
    if (gender === 'male') {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
    } else {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
    }
    
    // Multiply BMR by activity factor
    return Math.round(bmr * ACTIVITY_MULTIPLIERS[activityLevel]);
}

// Calculate Macronutrient Distribution
function calculateMacros(calories, fitnessGoal) {
    const ratios = MACRO_RATIOS[fitnessGoal];
    
    return {
        protein: Math.round((calories * ratios.protein) / 4), // 4 calories per gram of protein
        carbs: Math.round((calories * ratios.carbs) / 4),     // 4 calories per gram of carbs
        fat: Math.round((calories * ratios.fat) / 9)          // 9 calories per gram of fat
    };
}

// Calculate Daily Water Goal (in liters)
function calculateWaterGoal(weight, activityLevel) {
    // Base recommendation: 30-35ml per kg of body weight
    let baseWater = weight * 0.033;
    
    // Adjust for activity level
    const activityMultiplier = {
        'sedentary': 1.0,
        'lightly_active': 1.1,
        'moderately_active': 1.2,
        'very_active': 1.3,
        'extremely_active': 1.4
    };
    
    return Math.round(baseWater * activityMultiplier[activityLevel] * 10) / 10;
}

// Update form calculations in real-time
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('survey-form');
    const fields = ['weight', 'height', 'age', 'gender', 'activity_level', 'fitness_goal'];
    
    fields.forEach(field => {
        const element = document.getElementById(field);
        if (element) {
            element.addEventListener('change', updateCalculations);
        }
    });
    
    function updateCalculations() {
        const weight = parseFloat(document.getElementById('weight').value);
        const height = parseFloat(document.getElementById('height').value);
        const age = parseInt(document.getElementById('age').value);
        const gender = document.getElementById('gender').value;
        const activityLevel = document.getElementById('activity_level').value;
        const fitnessGoal = document.getElementById('fitness_goal').value;
        
        if (weight && height && age && gender && activityLevel && fitnessGoal) {
            // Calculate and display BMI
            const bmi = calculateBMI(weight, height);
            if (document.getElementById('bmi-display')) {
                document.getElementById('bmi-display').textContent = bmi;
            }
            
            // Calculate and display TDEE
            const tdee = calculateTDEE(weight, height, age, gender, activityLevel);
            if (document.getElementById('calorie-goal')) {
                document.getElementById('calorie-goal').value = tdee;
            }
            
            // Calculate and display macros
            const macros = calculateMacros(tdee, fitnessGoal);
            if (document.getElementById('protein-goal')) {
                document.getElementById('protein-goal').value = macros.protein;
            }
            if (document.getElementById('carbs-goal')) {
                document.getElementById('carbs-goal').value = macros.carbs;
            }
            if (document.getElementById('fat-goal')) {
                document.getElementById('fat-goal').value = macros.fat;
            }
            
            // Calculate and display water goal
            const waterGoal = calculateWaterGoal(weight, activityLevel);
            if (document.getElementById('water-goal')) {
                document.getElementById('water-goal').value = waterGoal;
            }
        }
    }
});
