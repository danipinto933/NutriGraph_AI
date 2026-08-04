from fastapi import APIRouter

from app.api.endpoints import admin, admin_diets, admin_allergens, admin_ingredients, admin_recipes, analytics, auth, meta, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/users", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["user"])
api_router.include_router(admin.router, prefix="/admin/users", tags=["admin"])
api_router.include_router(admin_diets.router, prefix="/admin/diet-types", tags=["admin_diets"])
api_router.include_router(admin_allergens.router, prefix="/admin/allergens", tags=["admin_allergens"])
api_router.include_router(admin_ingredients.router, prefix="/admin/ingredients", tags=["admin_ingredients"])
api_router.include_router(admin_recipes.router, prefix="/admin/recipes", tags=["admin_recipes"])
api_router.include_router(analytics.router, prefix="/admin/analytics", tags=["admin_analytics"])
api_router.include_router(meta.router, prefix="/meta", tags=["meta"])



