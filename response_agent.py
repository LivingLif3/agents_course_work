from neo4j import AsyncGraphDatabase
import asyncio
import random

GENERATE_PICTURE_BY_DESCRIPTION = "GENERATE_PICTURE_BY_DESCRIPTION"
ADD_ELEMENT_ON_PICTURE = "ADD_ELEMENT_ON_PICTURE"
COMPARE_PICTURE_WITH_ORIGINAL = "COMPARE_PICTURE_WITH_ORIGINAL"
ADD_PICTURE_TO_KNOWLEDGEBASE = "ADD_PICTURE_TO_KNOWLEDGEBASE"
FIND_PICTURE = "FIND_PICTURE"


class ResponseAgent:
    def __init__(self, driver, type_of_request):
        self.type_of_requests = [
            GENERATE_PICTURE_BY_DESCRIPTION,
            ADD_ELEMENT_ON_PICTURE,
            COMPARE_PICTURE_WITH_ORIGINAL,
            ADD_PICTURE_TO_KNOWLEDGEBASE,
            FIND_PICTURE,
        ]
        self.relations_of_agents_added_to_request_node = {
            FIND_PICTURE: "finded_picture"
        }
        self.type_of_request = type_of_request
        self.driver = driver

    def form_list_names(self, records, variable, field):
        list_names = []
        for record in records.records:
            list_names.append(record[variable]._properties[field])

        return list_names

    async def delete_relation(self, name):
        await self.driver.execute_query(
            "MATCH (r: Node {name: 'concept_request'})-[c:nrel_context]->(n: Node {name: '"
            + name
            + "'}) DELETE c"
        )

    async def get_path_to_pic(self):
        records = await self.driver.execute_query(
            "MATCH (r: Class {name: 'concept_request'})-[:nrel_context]->(n: Node)<-[:rrel_key_element]-(pic: Node {name: 'Pic. (' + n.name + ')'})-[:rrel_example]->(path: Text) RETURN path"
        )

        return self.form_list_names(records, "path", "content")

    async def get_pic_name(self):
        records = await self.driver.execute_query(
            "MATCH (r: Class {name: 'concept_request'})-[:nrel_context]->(n: Node) RETURN n"
        )

        return self.form_list_names(records, "n", "name")

    async def get_genres_pic(self):
        records = await self.driver.execute_query(
            "MATCH (r: Class {name: 'concept_request'})-[:nrel_context]->(n: Node)-[:nrel_genre]->(g: Node) RETURN n.name, g.name"
        )
        return records.records

    async def get_originality_percents(self):
        records = await self.driver.execute_query(
            "MATCH (r: Class {name: 'concept_request'})-[:nrel_originality]->(n: Node) RETURN n"
        )
        return self.form_list_names(records, "n", "name")

    async def gen_find_response(self):
        response = ""
        start_keys = [
            "Результат поиска",
            "Найдены следующие изображения",
            "Были найдены следующие изображения",
            "Агент нашёл следующие изображения",
        ]
        response += start_keys[random.randint(0, len(start_keys) - 1)] + ": "
        pathes = await self.get_path_to_pic()
        for path in pathes:
            if pathes[-1] != path:
                response += path + ", "
            else:
                response += path + "."
        return response

    async def gen_genre_response(self):
        response = ""
        start_keys = [
            "Найденные жанры",
            "Результат поиска",
            "Жанры для картин",
        ]
        response += start_keys[random.randint(0, len(start_keys) - 1)] + ": \n"
        genres = await self.get_genres_pic()
        genres_dict = {}
        for genre in genres:
            genres_dict[genre["n.name"]] = []
        for genre in genres:
            genres_dict[genre["n.name"]].append(genre["g.name"])
        for key in genres_dict:
            response += (
                "   Название картины: "
                + key
                + ", её жанры: "
                + ", ".join(genres_dict[key])
                + "\n"
            )
        return response

    async def gen_originality_response(self):
        response = "Оригинальность выбранного изображения в сравнении с изображением картины под названием: "
        names = await self.get_pic_name()
        originalities = await self.get_originality_percents()

        originality_data = ""

        for originality in originalities:
            originality_data = originality
            break

        for name in names:
            response += "'" + name + "' составляет " + originality_data + "%"
            return response


async def main():
    driver = AsyncGraphDatabase.driver(
        "bolt://localhost:7687", auth=("neo4j", "sasha1475369")
    )
    agent = ResponseAgent(driver, "DSADADS")
    # response = await agent.gen_find_response()
    # response = await agent.gen_genre_response()
    response = await agent.gen_originality_response()
    print(response)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
