FROM jazzdd/alpine-flask:python3

ENV AUTH_ENDPOINT=http://localhost:8000/auth/o/authorize/\
    TOKEN_ENDPOINT=http://docker.for.mac.host.internal:8000/auth/o/token/\
    VERIFY_ENDPOINT=http://docker.for.mac.host.internal:8000/buildings/\
    CLIENT_ID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\
    CLIENT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\
    SCOPES="building:read building:write"

ADD . /app
