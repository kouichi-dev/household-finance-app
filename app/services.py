

import crud
import auth


def create_user(db,user):
    hashed = auth.hash_password(user.password)
    user.password = hashed
    return crud.create_user(db,user) 

def update_user(db,user,user_id):
    hashed = auth.hash_password(user.password)
    user.password = hashed
    return crud.update_user(db,user,user_id)