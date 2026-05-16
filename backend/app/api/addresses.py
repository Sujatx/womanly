from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models import Address, AddressRead, User
from app.deps import get_current_user
from app.di_container import get as di_get

router = APIRouter()

@router.get("/", response_model=List[AddressRead])
def get_addresses(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Address).where(Address.user_id == current_user.id)
    return di_get("address_repo").list_by_user(session, current_user.id)

@router.post("/", response_model=AddressRead)
def create_address(
    address_in: Address,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Ensure user_id is set to current user
    address_in.user_id = current_user.id
    
    # If this is set as default, unset others
    if address_in.is_default:
        di_get("address_repo").unset_defaults(session, current_user.id)
            
    session.add(address_in)
    session.commit()
    session.refresh(address_in)
    return address_in

@router.put("/{address_id}", response_model=AddressRead)
def update_address(
    address_id: int,
    address_update: Address,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_address = session.get(Address, address_id)
    if not db_address or db_address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")
        
    update_data = address_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_address, key, value)
        
    if address_update.is_default:
        di_get("address_repo").unset_defaults(session, current_user.id, exclude_id=address_id)
            
    session.add(db_address)
    session.commit()
    session.refresh(db_address)
    return db_address

@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_address = session.get(Address, address_id)
    if not db_address or db_address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")
        
    session.delete(db_address)
    session.commit()
    return {"status": "success"}
