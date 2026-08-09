from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/transactions", tags=["Transactions"])

# ─── Create Transaction ──────────────────────────────────────

@router.post(
    "", 
    response_model=schemas.TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction_data: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_transaction = models.Transaction(
        title=transaction_data.title,
        amount=transaction_data.amount,
        type=transaction_data.type,
        category=transaction_data.category,
        date=transaction_data.date,
        owner_id=current_user.id
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

# ─── Get All Transactions ────────────────────────────────────

@router.get("", response_model=List[schemas.TransactionResponse])
def get_all_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.owner_id == current_user.id
    ).all()

    return transactions

# ─── Filter Transactions ─────────────────────────────────────
# NOTE: /filter must come BEFORE /{transaction_id}

@router.get("/filter", response_model=List[schemas.TransactionResponse])
def filter_transactions(
    type: Optional[str] = Query(None, description="income or expense"),
    category: Optional[str] = Query(None, description="Category name"),
    minimum_amount: Optional[float] = Query(None, description="Minimum amount"),
    maximum_amount: Optional[float] = Query(None, description="Maximum amount"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Start with current user's transactions
    query = db.query(models.Transaction).filter(
        models.Transaction.owner_id == current_user.id
    )

    # Apply filters dynamically
    if type:
        query = query.filter(models.Transaction.type == type)
    
    if category:
        query = query.filter(models.Transaction.category == category)
    
    if minimum_amount is not None:
        query = query.filter(models.Transaction.amount >= minimum_amount)
    
    if maximum_amount is not None:
        query = query.filter(models.Transaction.amount <= maximum_amount)

    return query.all()

# ─── Get Transaction By ID ───────────────────────────────────

@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )

    # Check ownership
    if transaction.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this transaction"
        )

    return transaction

# ─── Update Transaction ──────────────────────────────────────

@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int,
    update_data: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )

    # Check ownership
    if transaction.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this transaction"
        )

    # Apply updates (only provided fields)
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)

    return transaction

# ─── Delete Transaction ──────────────────────────────────────

@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )

    # Check ownership
    if transaction.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this transaction"
        )

    db.delete(transaction)
    db.commit()

    return {
        "status": 200,
        "message": f"Transaction {transaction_id} deleted successfully"
    }