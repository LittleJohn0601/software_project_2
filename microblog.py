# microblog.py
# flask app is set in this file

from blogapp import create_app

app = create_app()

if __name__ == '__main__':
    # 使用 0.0.0.0 允许外部访问（Docker 需要）
    app.run(debug=True, host='0.0.0.0', port=5001)