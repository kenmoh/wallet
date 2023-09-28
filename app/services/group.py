from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from app.models.models import Group, GroupMember
from app.schemas import group

# GROUP START


def create_new_group(user_id: str, user_group: group.CreateGroupSchema, db: Session):

    """
    Helper function to create a group
    """
    db_group = db.query(Group).filter(Group.group_name == user_group.group_name).all()

    # Check if a group exist
    if len(db_group) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Group with this name already exist.')
    # Create a group if not exist
    try:
        new_group: Group = Group(user_id=user_id, group_name=user_group.group_name, bill_amount=user_group.bill_amount,
                                 created_at=datetime.today())
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return new_group
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Something went wrong')


def all_groups_by_user(user_id: str, db: Session):
    """
    Helper function to get all groups by a single user from db
    """
    try:
        return db.query(Group).filter(Group.user_id == user_id).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Something went wrong.')


def all_groups(db: Session):
    """
    Get all groups from the database (Admin)
    """
    try:
        return db.query(Group).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Something went wrong.')


def get_group_by_user(user_id: str, group_id: str, db: Session):
    """
    Get a group from db ny user
    """
    return db.query(Group).filter(Group.id == group_id).filter(Group.user_id == user_id).first()


def update_group(user_id: str, group_id: str, db: Session, user_group: group.CreateGroupSchema):
    """
    Helper function to update a group by user
    """
    db_group = db.query(Group).filter(Group.id == group_id).first()

    if db_group.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid user')

    db_group.group_name = user_group.group_name
    db_group.bill_amount = user_group.bill_amount

    db.commit()
    db.refresh(db_group)

    return db_group


def delete_group_by_user(user_id: str, group_id: str, db: Session):

    """
    Delete a group from db by user
    """

    db_group = db.query(Group.id).filter(Group.id == group_id).first()

    if db_group.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid user')

    db.delete(db_group)
    db.commit()


# END GROUP


# GROUP MEMBER START

def create_new_member(user_id: str, group_id: str, db: Session, member: group.CreateGroupMemberSchema):
    """
    This function adds new member to group
    """

    db_member = db.query(GroupMember).filter(GroupMember.member_username == member.member_username).all()
    db_group = db.query(Group).filter(Group.id == group_id).first()
    amount_to_split = db_group.bill_amount

    # Check if member already exists
    if len(db_member) > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Member with this name already exist.')

    try:
        if member.percentage and member.amount:
            new_member = GroupMember(user_id=user_id, group_id=group_id, member_username=member.member_username,
                                     amount=amount_to_split*(member.percentage/100),
                                     percentage=member.percentage, created_at=datetime.today())
            db.add(new_member)
            db.commit()
            db.refresh(new_member)

            db.commit()
            db.refresh(db_group)

            return new_member

        if member.amount:
            new_member = GroupMember(user_id=user_id, group_id=group_id, member_username=member.member_username,
                                     amount=member.amount,
                                     percentage=member.percentage, created_at=datetime.today())
            db.add(new_member)
            db.commit()
            db.refresh(new_member)

            db_group.bill_amount -= new_member.amount

            db.commit()
            db.refresh(db_group)

            return new_member

        if member.percentage:
            new_member = GroupMember(user_id=user_id, group_id=group_id, member_username=member.member_username,
                                     amount=amount_to_split*(member.percentage/100),
                                     percentage=member.percentage, created_at=datetime.today())
            db.add(new_member)
            db.commit()
            db.refresh(new_member)

            db.commit()
            db.refresh(db_group)

            return new_member

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Something went wrong.')


