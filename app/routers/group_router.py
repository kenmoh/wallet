from fastapi import APIRouter, status, Depends
from app.database.database import session, get_db
from app.schemas import group as group_schema
from app.services import group
from app.utils.auth import get_current_user
from app.models.models import User


group_router = APIRouter(prefix='/api/group', tags=['Group'])

# GROUP ROUTES STARTS


@group_router.get('/', status_code=status.HTTP_200_OK)
async def get_all_groups(db: session = Depends(get_db)) -> list[group_schema.GroupResponseSchema]:
    """
    Get all groups in database
    """
    return group.all_groups(db)


@group_router.post('/', status_code=status.HTTP_201_CREATED)
async def add_group(user_group: group_schema.CreateGroupSchema, db: session = Depends(get_db), current_user: User = Depends(get_current_user)) -> (
        group_schema.GroupResponseSchema):
    """
    Create group
    """
    return group.create_new_group(user_id=current_user.id, user_group=user_group, db=db)


@group_router.get('/get-user-groups', status_code=status.HTTP_200_OK)
async def get_all_groups_by_user(current_user: User = Depends(get_current_user), db: session = Depends(get_db)) -> list[group_schema.GroupResponseSchema]:
    """ Get a group by current logged-in user """
    return group.all_groups_by_user(user_id=current_user.id, db=db)


@group_router.patch('/{group_id}/update-group', status_code=status.HTTP_202_ACCEPTED)
async def update_group_by_id(group_id: str, user_group: group_schema.CreateGroupSchema, current_user: User = Depends(get_current_user),
                             db: session = Depends(get_db)) -> group_schema.GroupResponseSchema:
    """
    Update group by id
    """
    return group.update_group(user_id=current_user.id, group_id=group_id, db=db, user_group=user_group)


@group_router.delete('/{group_id}/delete-group', status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_by_user(group_id: str, user_id: User = Depends(get_current_user), db: session = Depends(get_db)):
    """
    Delete group is exists
    """
    return group.delete_group_by_user(user_id=user_id.id, db=db, group_id=group_id)


# GROUP ROUTES ENDS


# MEMBERS ROUTE STARTS
@group_router.post('/add-member-to-group', status_code=status.HTTP_201_CREATED)
async def add_member_to_group(group_id: str, member: group_schema.CreateGroupMemberSchema, user_id: User = Depends(get_current_user),
                              db: session = Depends(get_db)) -> group_schema.GroupMemberResponseSchema:
    """
    Add new member to group
    """
    return group.create_new_member(user_id=user_id.id, group_id=group_id, db=db, member=member)
