from app.services.biometrics import calculate_bmi, calculate_bmr, calculate_tdee


def test_calculate_bmi():
    # Weight: 70kg, Height: 175cm -> BMI: 70 / (1.75^2) = 22.86
    assert calculate_bmi(70, 175) == 22.86

def test_calculate_bmr_male():
    # Weight: 70kg, Height: 175cm, Age: 30, Sex: m
    # (10 * 70) + (6.25 * 175) - (5 * 30) + 5 = 700 + 1093.75 - 150 + 5 = 1648.75
    assert calculate_bmr('m', 70, 175, 30) == 1648.75

def test_calculate_bmr_female():
    # Weight: 60kg, Height: 160cm, Age: 25, Sex: f
    # (10 * 60) + (6.25 * 160) - (5 * 25) - 161 = 600 + 1000 - 125 - 161 = 1314.0
    assert calculate_bmr('f', 60, 160, 25) == 1314.0

def test_calculate_tdee():
    bmr = 1500.0
    activity = 1.2 # Sedentary
    assert calculate_tdee(bmr, activity) == 1800.0
