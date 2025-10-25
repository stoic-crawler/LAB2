from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/add', methods=['GET'])
def add():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    return jsonify(result=a + b)

@app.route('/subtract', methods=['GET'])
def subtract():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    return jsonify(result=a - b)

@app.route('/multiply', methods=['GET'])
def multiply():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    return jsonify(result=a * b)

@app.route('/divide', methods=['GET'])
def divide():
    a = float(request.args.get('a'))
    b = float(request.args.get('b'))
    if b == 0:
        return jsonify(error="Division by zero"), 400
    return jsonify(result=a / b)
@app.route('/3wina', methods=['GET'])
def _3wina():
    return jsonify("i see you !")


if __name__ == '__main__':
    app.run(host='127.1', port=5000)