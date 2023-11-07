from neo4j import AsyncGraphDatabase
import asyncio


class SearchingAgent:
    uri = "bolt://localhost:7687"
    username = "ALIAKSANDR"
    password = "sasha1475369"

    result = None

    def __init__(self, author=False, name=False):
        self.driver = AsyncGraphDatabase.driver(self.uri, auth=("neo4j", self.password))
        self.author = author
        self.name = name

    def form_list_names(self, records):
        list_names = []
        for record in records:
            list_names.append(record["ns"]._properties["name"])

        return list_names

    async def find_picture_by_author(self, author):
        record = await self.driver.execute_query(
            "MATCH (n: Node {name: "
            + f"'{author}'"
            + "})-[:nrel_write]->(ns: Node) RETURN ns"
        )
        return self.form_list_names(record.records)

    async def find_picture_by_name(self, name):
        record = await self.driver.execute_query(
            "MATCH (ns: Node {name: " + f"'{name}'" + "}) RETURN ns"
        )
        return self.form_list_names(record.records)

    async def find_picture_by_author_and_name(self, author, name):
        record = await self.driver.execute_query(
            "MATCH (n: Node {name: "
            + f"'{author}'"
            + "})-[:nrel_write]->(ns: Node {name: "
            + f"'{name}'"
            + "}) RETURN ns"
        )
        records = record.records
        return self.form_list_names(records)
        # async with self.driver.session() as session:
        #     result = await session.run(
        #         "MATCH (n: Node {name: "
        #         + f"'{author}'"
        #         + "})-[:nrel_write]->(ns: Node {name: "
        #         + f"'{name}'"
        #         + "}) RETURN ns"
        #     )
        #     print(list(result), "LALALLA")
        #     await result.consume()
        #     return result

    async def find_picture(self, author=False, name=False):
        names = None
        if author and not name:
            names = await self.find_picture_by_author(author)
        elif name and author:
            names = await self.find_picture_by_author_and_name(author, name)
        else:
            names = await self.find_picture_by_name(name)

        return names

    # async def get_pic(self, name):
    #     async with self.driver.session() as session:
    #         result = await session.run(
    #             "MATCH (n: Node {name: 'Pic. ("
    #             + f"{name}"
    #             + ")'})-[:rrel_key_element]->(ns: Node {name: "
    #             + f"'{name}'"
    #             + "}) RETURN n"
    #         )
    #         record = await result.single()

    #     return record

    # async def get_path_to_pic(self, node_pic_name):
    #     async with self.driver.session() as session:
    #         result = await session.run(
    #             "MATCH (n: Node {name: '"
    #             + f"{node_pic_name}"
    #             + "'})-[:rrel_example]->(t: Text) RETURN t"
    #         )
    #         record = await result.single()

    #     return record

    # async def find_path_to_file(self):
    #     records = None
    #     if self.name or self.author:
    #         pathes = []

    #         records = await self.find_picture(author=self.author, name=self.name)

    #         for record in records:
    #             async with self.driver.session() as session:
    #                 picture = await self.get_pic(record["ns"]._properties["name"])
    #                 pathes.append(
    #                     (await self.get_path_to_pic(picture["n"]._properties["name"]))[
    #                         "t"
    #                     ]._properties["content"]
    #                 )

    #         return pathes

    # async def add_result_to_req_context(self):
    #     pathes = await self.find_path_to_file()

    #     for path in pathes:
    #         async with self.driver.session() as session:
    #             await session.run("CREATE (n: SearchPicture {path: '" + path + "'})")
    #             await session.run(
    #                 "CREATE (p: SearchPicture {path: '"
    #                 + path
    #                 + "'})-[:picture_path]->(r: Class {name: 'concept_request'})"
    #             )

    async def create_relationship_to_req(self, name):
        await self.driver.execute_query(
            "MATCH (p: Node {name: '"
            + name
            + "'}), (req: Class {name: 'concept_request'}) CREATE (req)-[:nrel_context]->(p)"
        )

        # await self.driver.execute_query(
        #     "CREATE (p: Node {name: '"
        #     + name
        #     + "'})<-[:finded_picture]-(r: Class {name: 'concept_request'})"
        # )

    async def add_picture_to_req_context(self):
        if self.name or self.author:
            names = await self.find_picture(author=self.author, name=self.name)

            for name in names:
                await self.create_relationship_to_req(name)


async def main():
    agent = SearchingAgent("Leonardo da Vinci", "Mona Lisa")
    await agent.add_picture_to_req_context()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
