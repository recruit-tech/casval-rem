from chalice import AuthResponse
import jwt
import os


def authorize(auth_request):
    try:
        scheme, token = auth_request.token.split()
        if scheme.lower() != "bearer":
            raise Exception
        claim = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
        return AuthResponse(routes=["*"], principal_id="", context=claim)

    except Exception as e:
        print(e)
        return AuthResponse(routes=[], principal_id="")
