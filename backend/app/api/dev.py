from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel, Session, select
from app.core.database import get_session, engine
from app.models import (
    User, UserCreate, UserResponse,
    Client, ClientCreate,
    ProjectState, ProjectStateCreate,
    Project, ProjectCreate,
    RequirementState, RequirementStateCreate,
    Requirement, RequirementCreate,
    ArticleState, ArticleStateCreate,
    Article, ArticleCreate,
    PaymentCondition, PaymentConditionCreate,
    Report, ReportCreate, ReportResponse
)
from datetime import datetime
from decimal import Decimal

router = APIRouter()

@router.post("/create-db-and-tables")
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    return {"message": "Database created successfully"}

@router.post("/reset-db")
def reset_database():
    SQLModel.metadata.drop_all(engine, checkfirst=False)
    SQLModel.metadata.create_all(engine)
    return {"message": "Database reset successfully"}

@router.post("/delete-db")
def delete_database():
    try:
        # drop tables
        SQLModel.metadata.drop_all(engine, checkfirst=False)

        return {"message": "Database deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-test-data")
def create_test_data():
    try:
        with get_session() as session:
            # 1. Create test user
            test_user = User(
                username="testuser",
                full_name="Test User",
                password_hash="hashedpassword123"
            )
            session.add(test_user)
            session.refresh(test_user)

            # 2. Create test client
            test_client = Client(
                name="Test Client"
            )
            session.add(test_client)
            session.refresh(test_client)

            # 3. Create test project state
            test_project_state = ProjectState(
                name="Test Project State",
                description="State for test projects",
                order=1,
                active=True
            )
            session.add(test_project_state)
            session.refresh(test_project_state)

            # 4. Create test project
            test_project = Project(
                number="TEST-001",
                name="Test Project",
                description="A test project",
                date=datetime.utcnow(),
                state_id=test_project_state.id,
                responsible_id=test_user.id,
                client_id=test_client.id
            )
            session.add(test_project)
            session.refresh(test_project)

            # 5. Create test requirement state
            test_requirement_state = RequirementState(
                name="Test Requirement State",
                description="State for test requirements",
                order=1,
                active=True
            )
            session.add(test_requirement_state)
            session.refresh(test_requirement_state)

            # 6. Create test requirement
            test_requirement = Requirement(
                project_id=test_project.id,
                request_date=datetime.utcnow(),
                requested_by=test_user.id,
                state_id=test_requirement_state.id
            )
            session.add(test_requirement)
            session.refresh(test_requirement)

            # 7. Create test article state
            test_article_state = ArticleState(
                name="Test Article State",
                description="State for test articles",
                order=1,
                active=True
            )
            session.add(test_article_state)
            session.refresh(test_article_state)

            # 8. Create test article
            test_article = Article(
                requirement_id=test_requirement.id,
                requirement_consecutive=1,
                quantity=Decimal("10.5"),
                unit="pcs",
                brand="Test Brand",
                model="Test Model",
                dimensions="10x20x30",
                state_id=test_article_state.id,
                notes="Test article notes"
            )
            session.add(test_article)
            session.refresh(test_article)

            # 9. Create test payment condition
            test_payment_condition = PaymentCondition(
                name="Test Payment Condition",
                description="Test payment condition description",
                text="Payment terms: 30 days",
                active=True
            )
            session.add(test_payment_condition)
            session.refresh(test_payment_condition)

            return {
                "message": "Test data created successfully",
                "data": {
                    "user_id": test_user.id,
                    "client_id": test_client.id,
                    "project_state_id": test_project_state.id,
                    "project_id": test_project.id,
                    "requirement_state_id": test_requirement_state.id,
                    "requirement_id": test_requirement.id,
                    "article_state_id": test_article_state.id,
                    "article_id": test_article.id,
                    "payment_condition_id": test_payment_condition.id
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users", response_model=list[UserResponse])
def get_users():
    with get_session() as session:
        statement = select(User)
        results = session.exec(statement)
        users = [user for user in results]
        return users
    
@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    with get_session() as session:
        db_user = User.model_validate(user)
        session.add(db_user)
        session.refresh(db_user)
        return db_user 