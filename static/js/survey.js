// Global variables
let currentStep = 1;
const totalSteps = 5;  // Updated to remove fitness section

// Form validation configuration
const validationRules = {
    age: {
        min: 13,
        max: 120,
        required: true
    },
    height: {
        min: 100,
        max: 250,
        required: true
    },
    weight: {
        min: 30,
        max: 300,
        required: true
    },
    target_weight: {
        min: 30,
        max: 300,
        required: true
    },
    daily_calories: {
        min: 1200,
        max: 8000,
        required: true
    },
    protein_ratio: {
        min: 10,
        max: 50,
        required: true
    },
    carbs_ratio: {
        min: 10,
        max: 70,
        required: true
    },
    fat_ratio: {
        min: 10,
        max: 50,
        required: true
    },
    water_target: {
        min: 1,
        max: 10,
        required: true
    },
    sleep_hours: {
        min: 4,
        max: 12,
        required: true
    }
};

// Initialize the form
document.addEventListener('DOMContentLoaded', () => {
    showStep(1);
    updateProgressBar();
    setupFormValidation();
    document.querySelectorAll('select[name$="_condition"], select[name$="medication"], select[name$="allergy"], select[name$="injury"]')
        .forEach(setupOptionHandler);
});

// Progress bar functions
function updateProgressBar() {
    const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
    document.querySelector('.step-progress-bar').style.width = `${progress}%`;
    
    // Update step circles
    document.querySelectorAll('.step-circle').forEach((circle, index) => {
        if (index + 1 < currentStep) {
            circle.classList.add('complete');
            circle.classList.remove('active');
        } else if (index + 1 === currentStep) {
            circle.classList.add('active');
            circle.classList.remove('complete');
        } else {
            circle.classList.remove('active', 'complete');
        }
    });
}

// Navigation functions
function showStep(step) {
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.add('hidden');
    });
    document.getElementById(`step${step}`).classList.remove('hidden');
    currentStep = step;
    updateProgressBar();
}

function nextStep(currentStep) {
    // Clear any existing error messages before validation
    const currentStepElement = document.getElementById(`step${currentStep}`);
    clearErrorMessages(currentStepElement);
    
    if (validateStep(currentStep)) {
        showStep(currentStep + 1);
    }
}

function previousStep(currentStep) {
    // Clear any error messages when going back
    const currentStepElement = document.getElementById(`step${currentStep}`);
    clearErrorMessages(currentStepElement);
    showStep(currentStep - 1);
}

// Validation functions
function validateStep(step) {
    const currentStepElement = document.getElementById(`step${step}`);
    const requiredFields = currentStepElement.querySelectorAll('[required]');
    let isValid = true;
    
    // Clear previous error messages
    clearErrorMessages(currentStepElement);
    
    // Validate required fields
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    // Additional validation for nutrition step
    if (step === 4 && isValid) {
        isValid = validateMacroRatios();
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const rules = validationRules[field.id];
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showError(field, 'This field is required');
        return false;
    }
    
    // Numeric validation for fields with min/max
    if (rules && (rules.min !== undefined || rules.max !== undefined)) {
        const numValue = parseFloat(value);
        
        if (isNaN(numValue)) {
            showError(field, 'Please enter a valid number');
            return false;
        }
        
        if (rules.min !== undefined && numValue < rules.min) {
            showError(field, `Value must be at least ${rules.min}`);
            return false;
        }
        
        if (rules.max !== undefined && numValue > rules.max) {
            showError(field, `Value must be no more than ${rules.max}`);
            return false;
        }
    }
    
    return true;
}

function showError(field, message) {
    // Remove any existing error messages first
    clearError(field);
    
    // Add new error message
    field.classList.add('error');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearError(field) {
    field.classList.remove('error');
    const errorMessages = field.parentNode.querySelectorAll('.error-message');
    errorMessages.forEach(error => error.remove());
}

function clearErrorMessages(container) {
    container.querySelectorAll('.error-message').forEach(error => error.remove());
    container.querySelectorAll('.error').forEach(field => field.classList.remove('error'));
}

// Add macro ratio validation
function validateMacroRatios() {
    const protein = parseFloat(document.getElementById('protein_goal').value) || 0;
    const carbs = parseFloat(document.getElementById('carbs_goal').value) || 0;
    const fat = parseFloat(document.getElementById('fat_goal').value) || 0;
    
    // Convert grams to calories using standard multipliers
    const proteinCals = protein * 4;  // 4 calories per gram of protein
    const carbsCals = carbs * 4;      // 4 calories per gram of carbs
    const fatCals = fat * 9;          // 9 calories per gram of fat
    
    const totalCals = proteinCals + carbsCals + fatCals;
    const targetCals = parseFloat(document.getElementById('daily_calorie_goal').value) || 0;
    
    // Allow for some margin of error (within 10% of target calories)
    const margin = targetCals * 0.1;
    if (Math.abs(totalCals - targetCals) > margin) {
        showError(document.getElementById('protein_goal'), 
            `Total calories from macros (${totalCals.toFixed(0)}) should be close to your daily goal (${targetCals})`);
        return false;
    }
    return true;
}

// Form validation setup
function setupFormValidation() {
    const form = document.getElementById('surveyForm');
    
    // Only add form submit validation
    form.addEventListener('submit', (e) => {
        const isValid = validateStep(currentStep);
        if (!isValid) {
            e.preventDefault();
        }
    });
}

// Handle "None" and "Other" option details
function setupOptionHandler(select) {
    select.addEventListener('change', function() {
        const container = this.closest('[id]');
        const detailsDiv = this.parentNode.querySelector('[id$="-details"]');
        const addButton = container.querySelector('button[onclick^="addHealthItem"]');
        
        if (this.value === 'NONE') {
            // Hide details and disable "Add another" button
            if (detailsDiv) detailsDiv.classList.add('hidden');
            if (addButton) addButton.style.display = 'none';
            
            // Remove any additional items
            const items = container.querySelectorAll('select').length;
            if (items > 1) {
                const allItems = container.querySelectorAll('select');
                for (let i = 1; i < allItems.length; i++) {
                    allItems[i].parentNode.remove();
                }
            }
        } else {
            // Show "Add another" button
            if (addButton) addButton.style.display = '';
            
            // Show details only for "OTHER"
            if (detailsDiv) {
                if (this.value === 'OTHER') {
                    detailsDiv.classList.remove('hidden');
                } else {
                    detailsDiv.classList.add('hidden');
                }
            }
        }
    });
}

// Health item management
function addHealthItem(containerType) {
    const container = document.getElementById(containerType);
    const firstSelect = container.querySelector('select');
    
    // Don't add if "None" is selected
    if (firstSelect.value === 'NONE') {
        return;
    }
    
    const template = firstSelect.parentNode.cloneNode(true);
    
    // Reset values
    template.querySelector('select').value = '';
    const details = template.querySelector('[id$="-details"]');
    if (details) {
        details.classList.add('hidden');
        details.querySelectorAll('input').forEach(input => input.value = '');
        details.querySelectorAll('select').forEach(select => select.value = '');
        details.querySelectorAll('input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);
    }
    
    // Add remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'text-sm text-red-600 hover:text-red-800 mt-2 ml-4';
    removeBtn.textContent = '- Remove';
    removeBtn.onclick = function() {
        template.remove();
    };
    template.appendChild(removeBtn);
    
    // Add the new item before the "Add another" button
    const addButton = container.querySelector('button[onclick^="addHealthItem"]');
    container.insertBefore(template, addButton);
    
    // Setup event listeners for the new select
    setupOptionHandler(template.querySelector('select'));
}

// Handle exercise type and sport selections
function setupActivitySelections() {
    // Setup handlers for exercise types
    document.querySelectorAll('select[name="exercise_type"]').forEach(select => {
        select.addEventListener('change', function() {
            const detailsDiv = this.parentNode.querySelector('#exercise-type-details');
            if (this.value === 'OTHER') {
                detailsDiv.classList.remove('hidden');
                detailsDiv.querySelector('input').required = true;
            } else {
                detailsDiv.classList.add('hidden');
                detailsDiv.querySelector('input').required = false;
            }
        });
    });

    // Setup handlers for preferred sports
    document.querySelectorAll('select[name="preferred_sport"]').forEach(select => {
        select.addEventListener('change', function() {
            const detailsDiv = this.parentNode.querySelector('#sport-details');
            if (this.value === 'OTHER') {
                detailsDiv.classList.remove('hidden');
                detailsDiv.querySelector('input').required = true;
            } else {
                detailsDiv.classList.add('hidden');
                detailsDiv.querySelector('input').required = false;
            }
        });
    });
}

// Add another exercise type
function addExerciseType() {
    const container = document.getElementById('exercise-types');
    const template = container.querySelector('.flex.flex-wrap').cloneNode(true);
    
    // Reset values
    template.querySelector('select').value = '';
    const details = template.querySelector('#exercise-type-details');
    if (details) {
        details.classList.add('hidden');
        details.querySelector('input').value = '';
        details.querySelector('input').required = false;
    }
    
    // Add remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'text-sm text-red-600 hover:text-red-800 mt-2';
    removeBtn.textContent = '- Remove';
    removeBtn.onclick = function() {
        template.remove();
    };
    template.appendChild(removeBtn);
    
    // Add the new item before the "Add another" button
    const addButton = container.querySelector('button[onclick="addExerciseType()"]');
    container.insertBefore(template, addButton);
    
    // Setup event listener for the new select
    setupActivitySelections();
}

// Add another preferred sport
function addPreferredSport() {
    const container = document.getElementById('preferred-sports');
    const template = container.querySelector('.flex.flex-wrap').cloneNode(true);
    
    // Reset values
    template.querySelector('select').value = '';
    const details = template.querySelector('#sport-details');
    if (details) {
        details.classList.add('hidden');
        details.querySelector('input').value = '';
        details.querySelector('input').required = false;
    }
    
    // Add remove button
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'text-sm text-red-600 hover:text-red-800 mt-2';
    removeBtn.textContent = '- Remove';
    removeBtn.onclick = function() {
        template.remove();
    };
    template.appendChild(removeBtn);
    
    // Add the new item before the "Add another" button
    const addButton = container.querySelector('button[onclick="addPreferredSport()"]');
    container.insertBefore(template, addButton);
    
    // Setup event listener for the new select
    setupActivitySelections();
}

// Initialize activity selections on page load
document.addEventListener('DOMContentLoaded', function() {
    setupActivitySelections();
});

// Initialize option handlers
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('select[name$="_condition"], select[name$="medication"], select[name$="allergy"], select[name$="injury"]')
        .forEach(setupOptionHandler);
});
