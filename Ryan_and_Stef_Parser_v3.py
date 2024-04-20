import json
import psycopg2

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="milestone3db",
            user="postgres",
            password="2321")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database connection error: {error}")

def parse_file(file_path, parse_function):
    print(f"Parsing {file_path.split('/')[-1]}...")
    with open(file_path, 'r') as f:
        count_line = 0
        for line in f:
            data = json.loads(line)
            parse_function(data)
            count_line += 1
        print(f"Parsed {count_line} lines")

def parseBusinessData(data, cur):
    is_open_bool = True if data['is_open'] == 1 else False
    sql_str = """INSERT INTO Business 
                 (business_id, name, address, state, city, zipcode, stars, num_reviews, is_open) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cur.execute(sql_str, (
        data['business_id'],
        data['name'],
        data.get('address', ''),
        data['state'],
        data['city'],
        data['postal_code'],
        data['stars'],
        data['review_count'],
        is_open_bool
    ))

    categories = data.get('categories', [])
    if categories:
        for category_name in categories:
            cur.execute("SELECT category_id FROM Category WHERE name = %s;", (category_name,))
            category_result = cur.fetchone()
            if category_result:
                category_id = category_result[0]
            else:
                cur.execute("INSERT INTO Category (name) VALUES (%s) RETURNING category_id;", (category_name,))
                category_id = cur.fetchone()[0]
            cur.execute("INSERT INTO BusinessCategory (business_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                        (data['business_id'], category_id))


def parseReviewData(data, cur):
    sql_str = "INSERT INTO Review (review_id, business_id, stars, text) VALUES (%s, %s, %s, %s)"
    cur.execute(sql_str, (
        data['review_id'],
        data['business_id'],
        data['stars'],
        data['text']
    ))

def parseUserData(data, cur):
    sql_str = "INSERT INTO YelpUser (user_id, review_count) VALUES (%s, %s)"
    cur.execute(sql_str, (
        data['user_id'],
        data['review_count']
    ))

def parseCheckinData(data, cur):
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
    conn = connect_to_db()
    if conn is None:
        return
    cur = conn.cursor()

    try:
        parse_file('./Yelp-CptS451/yelp_business.JSON', lambda data: parseBusinessData(data, cur))
        parse_file('./Yelp-CptS451/yelp_review.JSON', lambda data: parseReviewData(data, cur))
        parse_file('./Yelp-CptS451/yelp_user.JSON', lambda data: parseUserData(data, cur))
        parse_file('./Yelp-CptS451/yelp_checkin.JSON', lambda data: parseCheckinData(data, cur))
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
