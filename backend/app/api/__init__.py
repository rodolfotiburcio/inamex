from fastapi import APIRouter
from .users import router as users_router
from .clients import router as clients_router
from .project_states import router as project_states_router
from .projects import router as projects_router
from .requirement_states import router as requirement_states_router
from .requirements import router as requirements_router
from .article_states import router as article_states_router
from .articles import router as articles_router
from .payment_conditions import router as payment_conditions_router
from .order_statuses import router as order_statuses_router
from .dev import router as dev_router
from .suppliers import router as suppliers_router
from .addresses import router as addresses_router
from .article_order_statuses import router as article_order_statuses_router
from .orders import router as orders_router
from .article_orders import router as article_orders_router
from .reports import router as reports_router
from .dedicated_times import router as dedicated_times_router
from .photos import router as photos_router
from .contacts import router as contacts_router 
from .budgets import router as budgets_router

api_router = APIRouter()
api_router.include_router(dev_router, prefix="/dev", tags=["development"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(clients_router, prefix="/clients", tags=["clients"])
api_router.include_router(project_states_router, prefix="/project-states", tags=["project-states"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(requirement_states_router, prefix="/requirement-states", tags=["requirement-states"])
api_router.include_router(requirements_router, prefix="/requirements", tags=["requirements"])
api_router.include_router(article_states_router, prefix="/article-states", tags=["article-states"])
api_router.include_router(articles_router, prefix="/articles", tags=["articles"])
api_router.include_router(payment_conditions_router, prefix="/payment-conditions", tags=["payment-conditions"])
api_router.include_router(order_statuses_router, prefix="/order-statuses", tags=["order-statuses"])
api_router.include_router(suppliers_router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(addresses_router, prefix="/addresses", tags=["addresses"])
api_router.include_router(article_order_statuses_router, prefix="/article-order-statuses", tags=["article-order-statuses"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(article_orders_router, prefix="/article-orders", tags=["article-orders"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(dedicated_times_router, prefix="/dedicated-times", tags=["dedicated-times"])
api_router.include_router(photos_router, prefix="/photos", tags=["photos"])
api_router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
api_router.include_router(budgets_router, prefix="/budgets", tags=["budgets"])