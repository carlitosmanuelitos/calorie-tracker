import re
from typing import List, Optional

class PasswordValidator:
    def __init__(self):
        self.min_length = 8
        self.max_length = 50
        self.min_lowercase = 1
        self.min_uppercase = 1
        self.min_digits = 1
        self.min_special = 1
        self.special_chars = r"[!@#$%^&*(),.?\":{}|<>]"

    def validate(self, password: str) -> tuple[bool, Optional[List[str]]]:
        errors = []
        
        # Check length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        if len(password) > self.max_length:
            errors.append(f"Password must be at most {self.max_length} characters long")
            
        # Check lowercase
        if len(re.findall(r"[a-z]", password)) < self.min_lowercase:
            errors.append("Password must contain at least one lowercase letter")
            
        # Check uppercase
        if len(re.findall(r"[A-Z]", password)) < self.min_uppercase:
            errors.append("Password must contain at least one uppercase letter")
            
        # Check digits
        if len(re.findall(r"\d", password)) < self.min_digits:
            errors.append("Password must contain at least one digit")
            
        # Check special characters
        if len(re.findall(self.special_chars, password)) < self.min_special:
            errors.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
            
        return (len(errors) == 0, errors if errors else None)

password_validator = PasswordValidator()
