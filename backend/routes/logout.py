from fastapi import APIRouter, Response

router = APIRouter()

@router.post("/logout")
async def logout(response: Response):
    """
    Logout user by deleting authentication cookies.
    Deletes both access_token and shop_access_token cookies.
    """
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("shop_access_token", path="/")
    return {"message": "Logged out successfully"}
