import graphene
import home.queries


class Query(home.queries.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)

