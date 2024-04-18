import json
import psycopg2

def connect_to_db():
    try:
        # Connect to your PostgreSQL database on PgAdmin
        conn = psycopg2.connect(
            host="localhost",  # or another host if your database is on a different server
            database="milestone2db",
            user="postgres",  # Replace with your PgAdmin username
            password="2312")  # Replace with your PgAdmin password
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def cleanStr4SQL(s):
    return s.replace("'", "''").replace("\n", " ")

def getAttributes(attributes):
    L = []
    for (attribute, value) in list(attributes.items()):
        if isinstance(value, dict):
            L += getAttributes(value)
        else:
            L.append((attribute, value))
    return L

def parse_file(file_path, parse_function):
    print(f"Parsing {file_path.split('/')[-1]}...")
    with open(file_path, 'r') as f:
        count_line = 0
        for line in f:
            data = json.loads(line)
            parse_function(data)  # No need to pass outfile anymore
            count_line += 1
        print(f"Parsed {count_line} lines")


def parseBusinessData(data, cur):
    # Assuming is_open is 1 for open and 0 for closed in the JSON data
    is_open_bool = True if data['is_open'] == 1 else False

    # Preparing the SQL insert statement
    sql_str = """INSERT INTO Business 
                 (business_id, name, address, state, city, zipcode, stars, num_reviews, is_open) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cur.execute(sql_str, (
        data['business_id'],
        cleanStr4SQL(data['name']),
        cleanStr4SQL(data.get('address', '')),  # Using .get for optional attributes
        cleanStr4SQL(data['state']),
        data['city'],
        data['postal_code'],
        data['stars'],
        data['review_count'],
        is_open_bool  # Correctly casting to boolean based on the value
    ))
    
    # Handle category data
    categories = data.get('categories', [])
    for category_name in categories:
        # Check if the category exists
        cur.execute("SELECT category_id FROM Category WHERE name = %s;", (category_name,))
        category_result = cur.fetchone()

        if category_result:
            category_id = category_result[0]
        else:
            # Insert new category and retrieve its id
            cur.execute("INSERT INTO Category (name) VALUES (%s) RETURNING category_id;", (category_name,))
            category_id = cur.fetchone()[0]

        # Associate the business with the category
        cur.execute("INSERT INTO BusinessCategory (business_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;", 
                    (data['business_id'], category_id))


def parseReviewData(data, cur):
    # Preparing the SQL insert statement for the Review table
    sql_str = "INSERT INTO Review (review_id, business_id, stars, text) VALUES (%s, %s, %s, %s)"
    cur.execute(sql_str, (
        data['review_id'],
        data['business_id'],
        data['stars'],
        cleanStr4SQL(data['text'])
    ))

def parseUserData(data, cur):
    # Preparing the SQL insert statement for the YelpUser table
    # Please adjust the SQL table column names and the data fields according to your schema
    sql_str = "INSERT INTO YelpUser (user_id, review_count) VALUES (%s, %s)"
    cur.execute(sql_str, (
        data['user_id'],
        data['review_count']
    ))

def parseCheckinData(data, cur):
    # Preparing the SQL insert statement for the CheckIn table
    # Since each check-in entry is a combination of business_id, day, time, and count
    # you might want to consider restructuring the table or adjusting the parsing accordingly
    for day, times in data['time'].items():
        for hour, count in times.items():
            sql_str = "INSERT INTO CheckIn (business_id, day, time, num_checkins) VALUES (%s, %s, %s, %s)"
            cur.execute(sql_str, (
                data['business_id'],
                day,
                hour,
                count
            ))

def main():
    # Establish database connection
    conn = connect_to_db()
    cur = conn.cursor()

    try:
        # Example usage
        parse_file('./Yelp-CptS451/yelp_business.JSON', lambda data: parseBusinessData(data, cur))
        parse_file('./Yelp-CptS451/yelp_review.JSON', lambda data: parseReviewData(data, cur))
        parse_file('./Yelp-CptS451/yelp_user.JSON', lambda data: parseUserData(data, cur))
        parse_file('./Yelp-CptS451/yelp_checkin.JSON', lambda data: parseCheckinData(data, cur))

        # Commit changes if all operations were successful
        conn.commit()
    except Exception as e:
        # Log the exception and rollback changes
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        # Close cursor and connection in the end
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
