import psycopg2
from psycopg2 import sql
import csv
import os


class PostgreSQLManager:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self):
        """Connect to the PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            print("Connected to PostgreSQL Server")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")

    def close(self):
        """Close the cursor and connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("PostgreSQL connection closed.")

    def execute_query(self, query, params=None):
        """Execute a SQL query."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            print("Query executed successfully.")
        except psycopg2.Error as e:
            print(f"Error executing query: {e}")

    def fetch_all(self, query, params=None):
        """Fetch all rows from a query."""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            return None

    def create_table(self, table_name, columns):
        """
        Create a table with the specified columns.

        Args:
            table_name (str): Name of the table to create.
            columns (dict): Dictionary of column names and types.
        """
        try:
            # Replace spaces with underscores in column names
            sanitized_columns = {col.replace(" ", "_"): dtype for col, dtype in columns.items()}

            # Create column definitions
            columns_definition = ", ".join([f'"{col}" {dtype}' for col, dtype in sanitized_columns.items()])
            query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {columns_definition}
            );
            """
            self.execute_query(query)
        except psycopg2.Error as e:
            print(f"Error creating table '{table_name}': {e}")
            self.connection.rollback()  # Rollback the transaction

    def insert_data(self, table_name, data):
        """Insert data into a table."""
        try:
            columns = data.keys()
            values = tuple(data.values())
            query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({placeholders});").format(
                table=sql.Identifier(table_name),
                fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
                placeholders=sql.SQL(", ").join(sql.Placeholder() for _ in columns)
            )
            self.execute_query(query, values)
        except psycopg2.Error as e:
            print(f"Error inserting data: {e}")

    def update_data(self, table_name, updates, condition):
        """Update data in a table."""
        try:
            set_clause = ", ".join([f"{col} = %s" for col in updates.keys()])
            where_clause = " AND ".join([f"{col} = %s" for col in condition.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"
            params = tuple(updates.values()) + tuple(condition.values())
            self.execute_query(query, params)
        except psycopg2.Error as e:
            print(f"Error updating data: {e}")

    def list_tables(self):
        """List all tables in the current database."""
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
        """
        return self.fetch_all(query)

    def process_csv_and_insert(self, file_path):
        """
        Reads a CSV file, maps values to IDs in relevant tables, and inserts into source_target table.

        Args:
            file_path (str): Path to the CSV file.
        """
        try:
            # Open the CSV file
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)

                # Skip the header if present
                next(csv_reader, None)

                for row in csv_reader:
                    # Extract values from the CSV row
                    specie_name, source_name, target_name = row

                    # Map values to their respective IDs
                    self.cursor.execute("SELECT Id FROM species WHERE Specie_Name = %s", (specie_name,))
                    specie_id = self.cursor.fetchone()

                    self.cursor.execute("SELECT Id FROM source WHERE source_name = %s", (source_name,))
                    source_id = self.cursor.fetchone()

                    self.cursor.execute("SELECT Id FROM target WHERE target_name = %s", (target_name,))
                    target_id = self.cursor.fetchone()

                    # Check if all IDs were found
                    if not specie_id or not source_id or not target_id:
                        print(f"Error: Unable to find mapping for row: {row}")
                        continue

                    # Insert into source_target table
                    self.cursor.execute(
                        """
                        INSERT INTO source_target (specie_id, source_id, target_id)
                        VALUES (%s, %s, %s)
                        """,
                        (specie_id[0], source_id[0], target_id[0])
                    )

                # Commit the transaction
                self.connection.commit()
                print("Data from CSV file successfully inserted into source_target table.")

        except Exception as e:
            print(f"Error processing CSV file: {e}")
            self.connection.rollback()

    def process_directory_and_create_tables(self, directory_path):
        """
        Process files in a directory, extract file names and headers, and create PostgreSQL tables.

        Args:
            directory_path (str): Path to the directory containing files.
        """
        # Iterate through all folders and files
        for root, _, files in os.walk(directory_path):
            for file in files:
                # Remove '_merged.tsv' from the file name if it exists
                if file.endswith("_merged.tsv"):
                    file_name = file.replace("_merged.tsv", "")
                else:
                    file_name = file

                # Full file path
                file_path = os.path.join(root, file)

                # Extract headers if the file is a TSV file
                if file.endswith(".tsv"):
                    with open(file_path, mode="r", encoding="utf-8") as tsv_file:
                        first_line = tsv_file.readline().strip()  # Read the header line
                        headers = first_line.split("\t")  # Split headers by tab

                        # Keep only the first two headers
                        selected_headers = headers[:2]

                        # Add a primary key and foreign key column
                        headers_with_fk = {"Id": "SERIAL PRIMARY KEY"}
                        headers_with_fk.update({header: "TEXT" for header in selected_headers})
                        headers_with_fk["specie_id"] = "INTEGER REFERENCES species(Id)"

                        # Generate table name
                        table_name = file_name.lower()

                        # Check if the table already exists
                        if self.table_exists(table_name):
                            print(f"Table '{table_name}' already exists. Skipping.")
                            continue

                        # Create table in PostgreSQL
                        self.create_table(table_name, headers_with_fk)
                        print(f"Table '{table_name}' created successfully.")

    def table_exists(self, table_name):
        """
        Check if a table exists in the PostgreSQL database.

        Args:
            table_name (str): Name of the table to check.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = %s
        );
        """
        try:
            self.cursor.execute(query, (table_name,))
            return self.cursor.fetchone()[0]
        except psycopg2.Error as e:
            print(f"Error checking if table exists: {e}")
            self.connection.rollback()  # Rollback the transaction
            return False

    def drop_all_except_protected(self):
        """
        Drop all tables in the database except for the protected ones: species, source, target, source_target.
        """
        try:
            # Define the protected tables
            protected_tables = {"species", "source", "target", "source_target"}

            # Query to get all table names in the public schema
            query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
            """
            self.cursor.execute(query)
            tables = self.cursor.fetchall()

            # Iterate through all tables and drop those not in the protected list
            for (table_name,) in tables:
                if table_name not in protected_tables:
                    drop_query = f"DROP TABLE IF EXISTS {table_name} CASCADE;"
                    self.execute_query(drop_query)
                    print(f"Dropped table: {table_name}")

            print("All unprotected tables have been dropped.")
        except psycopg2.Error as e:
            print(f"Error dropping tables: {e}")
            self.connection.rollback()  # Rollback the transaction

    def insert_data_from_file(self, file_path, specie_id):
        """
        Read a single TSV file and insert data into the corresponding SQL table.

        Args:
            file_path (str): Path to the TSV file.
            specie_id (int): Specie ID to insert as a foreign key for each record.
        """
        # Extract the table name from the file name
        table_name = os.path.basename(file_path).replace("_merged.tsv", "").lower()

        try:
            with open(file_path, mode="r", encoding="utf-8") as tsv_file:
                reader = csv.reader(tsv_file, delimiter="\t")

                # Extract headers from the first row
                headers = next(reader)
                headers_with_specie = ["Id SERIAL PRIMARY KEY"] + headers + ["specie_id"]

                # Insert data row by row
                for row in reader:
                    if len(row) != len(headers):
                        print(f"Skipping malformed row in file {file_path}: {row}")
                        continue

                    row_with_specie = [None] + row + [specie_id]  # None for auto-increment Id
                    self.insert_into_table(table_name, headers_with_specie, row_with_specie)

            print(f"Data from file {file_path} inserted into table {table_name}.")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    def insert_data_from_files(self, folder_path, specie_id):
        """
        Read files from the specified folder and insert data into corresponding SQL tables.

        Args:
            folder_path (str): Path to the folder containing TSV files.
            specie_id (int): Specie ID to insert as a foreign key for each record.
        """
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith("_merged.tsv"):
                    table_name = file.replace("_merged.tsv", "").lower()
                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, mode="r", encoding="utf-8") as tsv_file:
                            reader = csv.reader(tsv_file, delimiter="\t")

                            # Extract headers from the first row
                            headers = next(reader)
                            selected_headers = headers[:2]  # Keep only the first two headers
                            headers_with_specie = selected_headers + ["specie_id"]

                            # Insert data row by row
                            for row in reader:
                                if len(row) < 2:  # Ensure at least two columns are present
                                    print(f"Skipping malformed row in file {file}: {row}")
                                    continue

                                selected_row = row[:2]  # Keep only the first two columns
                                row_with_specie = selected_row + [specie_id]  # Add specie_id
                                self.insert_into_table(table_name, headers_with_specie, row_with_specie)

                        print(f"Data from file {file} inserted into table {table_name}.")

                    except Exception as e:
                        print(f"Error processing file {file}: {e}")

    def insert_into_table(self, table_name, columns, values):
        """
        Insert a row of data into the specified table.

        Args:
            table_name (str): Name of the table.
            columns (list): List of column names.
            values (list): List of values corresponding to the columns.
        """
        try:
            # Build the INSERT query dynamically
            columns_sql = ", ".join([f'"{col}"' for col in columns])
            placeholders = ", ".join(["%s"] * len(values))
            query = f"INSERT INTO {table_name} ({columns_sql}) VALUES ({placeholders});"
            self.cursor.execute(query, values)
            self.connection.commit()

        except Exception as e:
            print(f"Error inserting into table {table_name}: {e}")
            self.connection.rollback()

    def get_all_species(self):
        query = "SELECT Id, Specie_Name FROM species;"
        result = self.fetch_all(query)
        return result if result else []

    def get_all_sources(self):
        query = "SELECT Id, source_name FROM source;"
        result = self.fetch_all(query)
        return result if result else []

    def get_all_targets(self):
        query = "SELECT Id, target_name FROM target;"
        result = self.fetch_all(query)
        return result if result else []

    def get_unique_relations_list(self):
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
            "ORDER BY table_name;"
        )
        tables = self.fetch_all(query)
        return [table[0] for table in tables] if tables else []

    def get_total_record_count(self):
        """
        Calculate the total number of records across all tables returned by get_unique_table_list.

        Returns:
            int: Total count of records from all tables.
        """
        table_list = self.get_unique_relations_list()
        if not table_list:
            print("No tables found.")
            return 0

        total_count = 0

        for table_name in table_list:
            count_query = f"SELECT COUNT(*) FROM {table_name};"
            try:
                result = self.fetch_all(count_query)
                if result:
                    total_count += result[0][0]
            except Exception as e:
                print(f"Error counting records in table {table_name}: {e}")

        return total_count

    def get_unique_relations_by_specie_list(self, specie_id):
        """
        Retrieve unique relations for a given species ID.

        Args:
            specie_id (int): The ID of the species to filter relations.

        Returns:
            list: A list of unique relations names for the specified species.
        """
        query = (
            "SELECT DISTINCT source.source_name || '_' || target.target_name AS table_name "
            "FROM source_target "
            "JOIN species ON species.id = source_target.specie_id "
            "JOIN source ON source.id = source_target.source_id "
            "JOIN target ON target.id = source_target.target_id "
            "WHERE source_target.specie_id = %s "
            "ORDER BY table_name;"
        )
        tables = self.fetch_all(query, (specie_id,))
        return [table[0] for table in tables] if tables else []

    def get_relation_counts_by_specie(self, specie_id):
        """
        Retrieve a list of relations (SQL table names) and their row counts for a given species ID.

        Args:
            specie_id (int): The ID of the species to filter relations.

        Returns:
            list: A list of tuples where each tuple contains (relation_name, row_count).
        """
        # Get the list of unique relations for the given species
        relations = self.get_unique_relations_by_specie_list(specie_id)
        relation_counts = []

        # Iterate over each relation and count rows
        for relation in relations:
            count_query = f"SELECT COUNT(*) FROM {relation};"
            try:
                result = self.fetch_all(count_query)
                if result:
                    relation_counts.append((relation, result[0][0]))
            except Exception as e:
                print(f"Error counting rows for relation {relation}: {e}")

        return relation_counts

    def get_all_relations_with_counts(self):
        """
        Retrieve a list of all relations (SQL table names) and their respective row counts.

        Returns:
            list: A list of tuples where each tuple contains (relation_name, row_count).
        """
        table_list = self.get_unique_relations_list()
        if not table_list:
            print("No tables found.")
            return []

        relations_with_counts = []

        for table_name in table_list:
            count_query = f"SELECT COUNT(*) FROM {table_name};"
            try:
                result = self.fetch_all(count_query)
                if result:
                    relations_with_counts.append((table_name, result[0][0]))
            except Exception as e:
                print(f"Error counting records in table {table_name}: {e}")

        return relations_with_counts

    def get_all_species_relation_summary(self):
        """
        Retrieve a summary for all species, including the species name,
        number of total relations, and the total counts of all relations.

        Returns:
            list: A list of tuples, where each tuple contains (specie_name, total_relations, total_counts).
        """
        # Get all species IDs and names
        species_query = "SELECT Id, Specie_Name FROM species;"
        species = self.fetch_all(species_query)

        if not species:
            print("No species found.")
            return []

        summary = []

        for specie_id, specie_name in species:
            # Get the list of relations for the species
            relations = self.get_unique_relations_by_specie_list(specie_id)
            total_relations = len(relations)

            # Calculate the total counts of all relations
            total_counts = 0
            for relation in relations:
                count_query = f"SELECT COUNT(*) FROM {relation} WHERE specie_id = %s;"
                try:
                    result = self.fetch_all(count_query, (specie_id,))
                    if result:
                        total_counts += result[0][0]
                except Exception as e:
                    print(f"Error counting rows for relation {relation}: {e}")

            # Add the summary for the current species
            summary.append((specie_name, total_relations, total_counts))

        return summary

    def get_sources_by_specie_id(self, specie_id):
        """
        Retrieve a list of sources and their IDs for a given species ID.

        Args:
            specie_id (int): The ID of the species to filter sources.

        Returns:
            list: A list of tuples where each tuple contains (source_id, source_name).
        """
        query = (
            "SELECT DISTINCT source.id, source.source_name "
            "FROM source_target "
            "JOIN species ON species.id = source_target.specie_id "
            "JOIN source ON source.id = source_target.source_id "
            "WHERE source_target.specie_id = %s "
            "ORDER BY source.source_name;"
        )
        result = self.fetch_all(query, (specie_id,))
        return result if result else []


# Example usage
if __name__ == "__main__":
    db_manager = PostgreSQLManager(

    )

    db_manager.connect()

    # Example: Create a table
    # db_manager.create_table("species", {
    #     "id": "SERIAL PRIMARY KEY",
    #     "name": "VARCHAR(100)",
    #     "habitat": "VARCHAR(100)"
    # })

    # # Example: Insert data
    # db_manager.insert_data("species", {
    #     "name": "Tiger",
    #     "habitat": "Forest"
    # })

    # # Example: Update data
    # db_manager.update_data("species", {"name": "Lion"}, {"id": 1})

    # Example: Fetch all data
    # db_manager.process_csv_and_insert("/netscratch/smunir/repositories/Clean_Databases/CTD/yeast.csv")
    # directory_path = "/curatime/Merged_Triples"
    # db_manager.process_directory_and_create_tables(directory_path)
    # db_manager.drop_all_except_protected()
    # folder = "/curatime/Merged_Triples/human_triples"
    # specie_id = 3
    # db_manager.insert_data_from_files(folder, specie_id)
    # folder="/curatime/Merged_Triples/thaliana_triples/lncRNA_miRNA_merged.tsv"
    # db_manager.insert_data_from_file(folder,specie_id)
    db_manager.close()
