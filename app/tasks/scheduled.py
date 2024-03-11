from app.tasks.celery_app import app_celery as app


@app.task(name="periodic_parser")
def parser():
    print("parsed")