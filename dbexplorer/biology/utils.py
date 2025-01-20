from django.db import connection

def fetch_all(query):
    """
    Executes a raw SQL query and returns all results as a list of dictionaries.
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in result]

def get_all_species():
    query = "SELECT Id, Specie_Name FROM species order by Specie_Name ASC;"
    result = fetch_all(query)
    return result if result else []

def get_sources_by_specie_id(specie_id):
    query = (
        "SELECT DISTINCT source.id, source.source_name "
        "FROM source_target "
        "JOIN species ON species.id = source_target.specie_id "
        "JOIN source ON source.id = source_target.source_id "
        "WHERE source_target.specie_id = " + str(specie_id) + " "
        "ORDER BY source.source_name;"
    )
    result = fetch_all(query)
    return result if result else []

def get_target_by_source_and_specie_id(specie_id, source_id):
    query = (
        "SELECT DISTINCT target.id, target.target_name "
        "FROM source_target "
        "JOIN species ON species.id = source_target.specie_id "
        "JOIN target ON target.id = source_target.target_id "
        "WHERE source_target.specie_id = " + str(specie_id) + " "
        "AND source_target.source_id = " + str(source_id) + " "
        "ORDER BY target.target_name;"
    )
    result = fetch_all(query)
    return result if result else []

def get_unique_relations_list(specie_id,source_id,target_id):
        """
        Retrieve unique relations from the given query.

        Returns:
            list: A list of unique relations names.
        """
        query = (
            "SELECT DISTINCT source.source_name || '_' || target.target_name AS table_name "
            "FROM source_target "
            "JOIN species ON species.id = source_target.specie_id "
            "JOIN source ON source.id = source_target.source_id "
            "JOIN target ON target.id = source_target.target_id "
            "WHERE source_target.specie_id = " + str(specie_id) + " " 
            "AND source_target.source_id = " + str(source_id) + " "
            "AND source_target.target_id = " + str(target_id) + " "
            "ORDER BY table_name;"
        )
        tables = fetch_all(query)
        data_query = "SELECT * from "+ tables[0]["table_name"] +" WHERE specie_id = " + str(specie_id) + " LIMIT 10;"
        data = fetch_all(data_query)
        return [d[0] for d in data] if data else []
