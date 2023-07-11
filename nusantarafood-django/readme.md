# Nusantarafood Django
Backend application that handles business logic and database operations

# Installation
1. Clone the repository
    ```
    git clone https://github.com/hardymanm/nusantarafood.git
    ```

2. Create and activate virtual environment
    On linux:
    ```
    cd nusantarafood/nusantarafood-django
    python3 -m venv venv
    source venv/bin/activate
    ```
    On windows:
     ```
    cd nusantarafood\nusantarafood-django
    python3 -m venv venv
    venv\Scripts\activate.bat

    ```

3. Install dependencies
    ```
    pip install -r requirements.txt
    ```

4. Copy database
    ```
    scp root@nusantarafoodkg.com:/root/db.sqlite3 db.sqlite3
    ```

5. Run django web server
    ```
    python manage.py runserver
    ```
