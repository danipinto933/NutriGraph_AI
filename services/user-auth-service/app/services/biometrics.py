from app.schemas.biometrics import BiometricProfile


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100.0
    if height_m <= 0:
        return 0.0
    return round(weight_kg / (height_m ** 2), 2)

def calculate_bmr(sex: str, weight_kg: float, height_cm: float, age_years: int) -> float:
    # Mifflin-St Jeor Equation
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years)
    if sex.lower() == 'm':
        bmr = base + 5
    else:
        bmr = base - 161
    return round(bmr, 2)

def calculate_tdee(bmr: float, activity_factor: float) -> float:
    return round(bmr * activity_factor, 2)

def get_biometric_profile(sex: str, weight_kg: float, height_cm: float, age_years: int, activity_factor: float) -> BiometricProfile:
    bmi = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(sex, weight_kg, height_cm, age_years)
    tdee = calculate_tdee(bmr, activity_factor)
    return BiometricProfile(bmi=bmi, bmr=bmr, tdee=tdee)
