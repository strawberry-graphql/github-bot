import uvicorn
from starlette.applications import Starlette

from app.schema import schema
from app.views import GraphQL

app = Starlette(debug=False)
app.add_route("/graphql", GraphQL(schema))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, access_log=False)  # noqa: S104
