# CampusCompanion

## Running CampusCompanion

1. ChromaDB is running on docker, use docker compose
    `docker compose up &`

2. To run the backend server:
    `./server/runserver.sh`

    * Add `.env` file.
    * Run `python manage.py makemigrations`
    * run `chmod +x runserver` if needed. 
    * The backend server will be running at port 1234.
    * See APIs in `http://127.0.0.1:1234/swagger/`
        * chatbot/upload/{file_path} upload student's pdf transcript
        * loader/{file_path} upload a dataset

3. To run the UI
    * `cd UI`
    * `npm install`
    * `npm run dev`

## Testing
Test code in `test`:

* `generator.py` is for Synthetic data generation. It generate student's information and save into `student_info.json`.
* `stuModel.py` provides `StuModel` to act as a Student to interact with Advior and use Scoring Evaluator to evaluate the result.

