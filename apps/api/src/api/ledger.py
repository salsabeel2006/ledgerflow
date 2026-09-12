from typing import Annotated
from decimal import Decimal
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db_session
from ..models.user import User
from ..models.ledger import Account, Transaction
from ..schemas.ledger import (
    AccountCreate,
    AccountResponse,
    TransactionCreate,
    TransactionResponse,
)
from .auth import get_current_user

router = APIRouter(prefix="/ledger", tags=["Ledger Accounts"])


class DepositRequest(BaseModel):
    account_id: str
    amount: Decimal


@router.post(
    "/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED
)
async def create_account(
    account_in: AccountCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Account:
    new_account = Account(user_id=current_user.id, currency=account_in.currency)
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    return new_account


@router.get("/accounts/me", response_model=list[AccountResponse])
async def get_my_accounts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    query = select(Account).where(Account.user_id == current_user.id)
    res = await db.execute(query)
    return res.scalars().all()


@router.post("/deposit", response_model=AccountResponse)
async def deposit_funds(
    deposit_in: DepositRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    query = select(Account).where(
        Account.id == deposit_in.account_id, Account.user_id == current_user.id
    )
    res = await db.execute(query)
    acc = res.scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    acc.balance += deposit_in.amount
    await db.commit()
    await db.refresh(acc)
    return acc


@router.post(
    "/transfer",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def transfer_funds(
    transfer_in: TransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> Transaction:
    if transfer_in.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transfer amount must be positive",
        )

    source_query = select(Account).where(Account.id == transfer_in.from_account_id)
    source_res = await db.execute(source_query)
    source_acc = source_res.scalar_one_or_none()

    if not source_acc or source_acc.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found or access denied",
        )

    if source_acc.balance < transfer_in.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds"
        )

    dest_query = select(Account).where(Account.id == transfer_in.to_account_id)
    dest_res = await db.execute(dest_query)
    dest_acc = dest_res.scalar_one_or_none()

    if not dest_acc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination account not found",
        )

    source_acc.balance = source_acc.balance - transfer_in.amount
    dest_acc.balance = dest_acc.balance + transfer_in.amount

    tx = Transaction(
        from_account_id=source_acc.id,
        to_account_id=dest_acc.id,
        amount=transfer_in.amount,
        status="completed",
    )
    db.add(tx)
    await db.commit()
    await db.refresh(source_acc)
    await db.refresh(dest_acc)
    await db.refresh(tx)
    return tx


@router.get("/transactions/{account_id}", response_model=list[TransactionResponse])
async def get_transactions(
    account_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
):
    query = (
        select(Transaction)
        .where(
            or_(
                Transaction.from_account_id == account_id,
                Transaction.to_account_id == account_id,
            )
        )
        .order_by(Transaction.timestamp.desc())
    )
    res = await db.execute(query)
    return res.scalars().all()