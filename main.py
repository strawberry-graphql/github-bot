import uvicorn
from starlette.applications import Starlette
from strawberry.asgi import GraphQL

from app.schema import schema

app = Starlette(debug=False)
app.add_route("/graphql", GraphQL(schema))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, access_log=False)
