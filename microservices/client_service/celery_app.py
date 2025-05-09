from celery import Celery

celery_app = Celery(
    'client_service',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

celery_app.conf.update(
    imports=['microservices.client_service.tasks']
)

# from celery import Celery

# celery_app = Celery(
#     'client_service',
#     broker='redis://localhost:6379/0',
#     backend='redis://localhost:6379/0'
# )

# celery_app.conf.task_routes = {
#     'client_service.tasks.*': {'queue': 'default'},
# }
