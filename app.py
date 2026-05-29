from flask import Flask,request,jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error,IntegrityError
app=Flask(__name__)
CORS(app)
db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="Krishna@9949",
    database="grade_tracker"
)
cursor=db.cursor(dictionary=True)

def calculate_grade(percentage):
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'

def get_remarks(grade):
    remarks = {
        "A": "Outstanding",
        "B": "Well done",
        "C": "Keep improving",
        "D": "Needs attention",
        "F": "Please seek help"
    }

    return remarks.get(grade, "")

def calculate_percentage(score, max_score):
    return round((float(score) / float(max_score)) * 100, 2)
@app.route("/students", methods=["GET"])
def get_students():

    try:
        name = request.args.get("name")

        if name:
            query = "SELECT * FROM students WHERE name LIKE %s"
            cursor.execute(query, (f"%{name}%",))
        else:
            query = "SELECT * FROM students"
            cursor.execute(query)

        students = cursor.fetchall()

        return jsonify(students), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400
    
@app.route("/students/<int:id>", methods=["GET"])
def get_student(id):

    try:
        query = "SELECT * FROM students WHERE id=%s"

        cursor.execute(query, (id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify(student), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


@app.route("/students", methods=["POST"])
def add_student():

    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")

        if not name or not email:
            return jsonify({
                "error": "Name and email are required"
            }), 400

        query = """
        INSERT INTO students (name, email)
        VALUES (%s, %s)
        """

        cursor.execute(query, (name, email))

        db.commit()

        return jsonify({
            "message": "Student added successfully"
        }), 201

    except IntegrityError:
        return jsonify({
            "error": "Email already exists"
        }), 409

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400
    
@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):

    try:
        data = request.get_json()

        name = data.get("name")
        email = data.get("email")

        query = "SELECT * FROM students WHERE id=%s"

        cursor.execute(query, (id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        update_query = """
        UPDATE students
        SET name=%s, email=%s
        WHERE id=%s
        """

        cursor.execute(update_query, (name, email, id))

        db.commit()

        return jsonify({
            "message": "Student updated successfully"
        }), 200

    except IntegrityError:
        return jsonify({
            "error": "Email already exists"
        }), 409

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):

    try:
        query = "SELECT * FROM students WHERE id=%s"

        cursor.execute(query, (id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        delete_query = "DELETE FROM students WHERE id=%s"

        cursor.execute(delete_query, (id,))

        db.commit()

        return jsonify({
            "message": "Student deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400
    
@app.route("/students/<int:id>/marks", methods=["GET"])
def get_marks(id):

    try:
        student_query = "SELECT * FROM students WHERE id=%s"

        cursor.execute(student_query, (id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        subject = request.args.get("subject")

        if subject:
            query = """
            SELECT * FROM marks
            WHERE student_id=%s AND subject=%s
            """

            cursor.execute(query, (id, subject))

        else:
            query = """
            SELECT * FROM marks
            WHERE student_id=%s
            """

            cursor.execute(query, (id,))

        marks = cursor.fetchall()

        result = []

        for mark in marks:

            percentage = calculate_percentage(
                mark["score"],
                mark["max_score"]
            )

            grade = calculate_grade(percentage)

            result.append({
                "id": mark["id"],
                "subject": mark["subject"],
                "score": float(mark["score"]),
                "max_score": float(mark["max_score"]),
                "percentage": percentage,
                "grade": grade,
                "remarks": get_remarks(grade)
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400

@app.route("/students/<int:id>/marks", methods=["POST"])
def add_marks(id):

    try:
        student_query = "SELECT * FROM students WHERE id=%s"

        cursor.execute(student_query, (id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        data = request.get_json()

        subject = data.get("subject")
        score = data.get("score")
        max_score = data.get("max_score", 100)

        if not subject or score is None:
            return jsonify({
                "error": "Subject and score are required"
            }), 400

        score = float(score)
        max_score = float(max_score)

        if score < 0 or score > max_score:
            return jsonify({
                "error": "Invalid score"
            }), 400

        query = """
        INSERT INTO marks (student_id, subject, score, max_score)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (id, subject, score, max_score))

        db.commit()

        percentage = calculate_percentage(score, max_score)

        grade = calculate_grade(percentage)

        return jsonify({
            "message": "Marks added successfully",
            "percentage": percentage,
            "grade": grade,
            "remarks": get_remarks(grade)
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400

@app.route("/marks/<int:id>", methods=["DELETE"])
def delete_mark(id):

    try:
        query = "SELECT * FROM marks WHERE id=%s"

        cursor.execute(query, (id,))

        mark = cursor.fetchone()

        if not mark:
            return jsonify({
                "error": "Mark not found"
            }), 404

        delete_query = "DELETE FROM marks WHERE id=%s"

        cursor.execute(delete_query, (id,))

        db.commit()

        return jsonify({
            "message": "Mark deleted successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400

@app.route("/students/<int:id>/report", methods=["GET"])
def student_report(id):

    try:
        student_query = "SELECT * FROM students WHERE id=%s"

        cursor.execute(student_query, (id,))

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        marks_query = """
        SELECT * FROM marks
        WHERE student_id=%s
        """

        cursor.execute(marks_query, (id,))

        marks = cursor.fetchall()

        if not marks:
            return jsonify({
                "message": "No marks found for student"
            }), 200

        subjects = []

        total_percentage = 0

        best_subject = None
        weakest_subject = None

        highest = -1
        lowest = 101

        for mark in marks:

            percentage = calculate_percentage(
                mark["score"],
                mark["max_score"]
            )

            grade = calculate_grade(percentage)

            total_percentage += percentage

            if percentage > highest:
                highest = percentage
                best_subject = mark["subject"]

            if percentage < lowest:
                lowest = percentage
                weakest_subject = mark["subject"]

            subjects.append({
                "subject": mark["subject"],
                "score": float(mark["score"]),
                "max_score": float(mark["max_score"]),
                "percentage": percentage,
                "grade": grade,
                "remarks": get_remarks(grade)
            })

        average_percentage = round(
            total_percentage / len(subjects),
            2
        )

        overall_grade = calculate_grade(average_percentage)

        status = "Pass"

        if overall_grade == "F":
            status = "Fail"

        report = {
            "student": {
                "id": student["id"],
                "name": student["name"],
                "email": student["email"]
            },
            "subjects": subjects,
            "average_percentage": average_percentage,
            "overall_grade": overall_grade,
            "status": status,
            "best_subject": best_subject,
            "weakest_subject": weakest_subject
        }

        return jsonify(report), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


@app.route("/summary", methods=["GET"])
def summary():

    try:
        students_query = "SELECT * FROM students"

        cursor.execute(students_query)

        students = cursor.fetchall()

        total_students = len(students)

        if total_students == 0:
            return jsonify({
                "message": "No students found"
            }), 200

        grade_counts = {
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
            "F": 0
        }

        student_averages = []

        class_total = 0

        pass_count = 0
        fail_count = 0

        for student in students:

            marks_query = """
            SELECT * FROM marks
            WHERE student_id=%s
            """

            cursor.execute(marks_query, (student["id"],))

            marks = cursor.fetchall()

            if not marks:
                average = 0

            else:
                total = 0

                for mark in marks:

                    percentage = calculate_percentage(
                        mark["score"],
                        mark["max_score"]
                    )

                    total += percentage

                average = round(total / len(marks), 2)

            class_total += average

            grade = calculate_grade(average)

            grade_counts[grade] += 1

            if grade == "F":
                fail_count += 1
            else:
                pass_count += 1

            student_averages.append({
                "name": student["name"],
                "average": average,
                "grade": grade
            })

        class_average = round(
            class_total / total_students,
            2
        )

        highest_student = max(
            student_averages,
            key=lambda x: x["average"]
        )

        lowest_student = min(
            student_averages,
            key=lambda x: x["average"]
        )

        ranked_students = sorted(
            student_averages,
            key=lambda x: x["average"],
            reverse=True
        )

        response = {
            "total_students": total_students,
            "class_average_percentage": class_average,
            "grade_counts": grade_counts,
            "highest_scoring_student": highest_student,
            "lowest_scoring_student": lowest_student,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "rankings": ranked_students
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


if __name__ == "__main__":
    app.run(debug=True)