import arrow
from fastapi import APIRouter
from app.db import db

# seed data
from app.data import MAIN_GROUPS, TIMEZONE, \
    MAIN_COURSES, ELECTIVE_COURSES, MAIN_SLOTS, \
    SNE_SLOTS, MS_ELECTIVE_SLOTS, SNE_COURSES, \
    B20_ELECTIVE_SLOTS, B19_ELECTIVE_SLOTS, \
    MS_ELECTIVE_NAMES, BS4_ELECTIVE_NAMES, BS3_ELECTIVE_NAMES, \
    RFL_COURSES, RFL_SLOTS, ORIGINAL_RELEVANT_INNO_SCHEDULE_USERS

router = APIRouter(tags=["Seed"], prefix="")


@router.get('/seed_group')
def seed_group():
    for key in MAIN_GROUPS:
        for group in MAIN_GROUPS[key]:
            db.group.create({
                "level_name": key, "specific_group": group
            })
    return {"message": "successful"}


@router.get('/seed_subscribed_users')
def seed_subscribed_users():
    db.user.create_many(
        data=list(map(lambda x: {"id": x}, ORIGINAL_RELEVANT_INNO_SCHEDULE_USERS)))
    return {"message": "successful"}


@router.get('/seed_course')
def seed_course():
    # SNE_COURSES, MAIN_COURSES, ELECTIVE_COURSES
    for course in ELECTIVE_COURSES:
        if not course["for_all_sub_groups"]:
            # get the ids of all groups in 'sub_groups' attribute
            course_groups_ids = []
            specific_groups = course['sub_groups']
            for name in specific_groups:
                group = db.group.find_first(
                    where={"level_name": course['groups'], "specific_group": name})
                course_groups_ids.append({"id": group.id})
            # create course and connect groups by id
            db.course.create(data={
                "description": course["description"],
                "is_elective": course["is_elective"],
                # "groups": {
                #     "connect": course_groups_ids
                # }
            })
        else:
            group_name = course["groups"]
            course_groups = db.group.find_many(
                where={"level_name": group_name})
            print(course_groups)
            course_groups_ids = list(
                map(lambda course: {"id": course.id}, course_groups))
            print(course_groups_ids)
            db.course.create(data={
                "description": course["name"],
                "is_elective": False,
                "groups": {
                    "connect": course_groups_ids
                }
            })
    return {"message": "successful"}


@router.get('/seed_russian_course')
def seed_russian_course():
    for course in RFL_COURSES:
        # create course and connect groups by id
        db.course.create(data={
            "description": course["description"],
            "is_elective": course["is_elective"],
            "short_name": course["short_name"],
        })
    return {"message": "successful"}


@router.get('/seed_slot')
def seed_slot():
    # MAIN_SLOTS, SNE_SLOTS, RFL_SLOTS
    db.slot.create_many(data=RFL_SLOTS)
    return {"message": "successful"}


@router.get('/duplicate_main_course_slots')
def duplicate_main_course_slots():
    new_slots = db.slot.find_many(where={
        "specific_group": {
            "not_in": ["M22-SNE-01", "B20", "B19", "M22"]
        }})
    new_slots = list(map(lambda x: {
        "instructor_name": x.instructor_name,
        "room_number": x.room_number,
        "start_time": arrow.get(x.start_time).to(TIMEZONE).shift(weeks=+1).isoformat(),
        "end_time": arrow.get(x.end_time).to(TIMEZONE).shift(weeks=+1).isoformat(),
        "course_id": x.course_id,
        "course_name": x.course_name,
        "type": x.type,
        "group_id": x.group_id,
        "specific_group": x.specific_group,
    }, new_slots))
    # db.slot.create_many(data=new_slots)

    for _ in range(3, 10):
        new_slots = list(map(lambda x: {
            "instructor_name": x["instructor_name"],
            "room_number": x["room_number"],
            "start_time": arrow.get(x["start_time"]).to(TIMEZONE).shift(weeks=+1).isoformat(),
            "end_time": arrow.get(x["end_time"]).to(TIMEZONE).shift(weeks=+1).isoformat(),
            "course_id": x["course_id"],
            "course_name": x["course_name"],
            "type": x["type"],
            "group_id": x["group_id"],
            "specific_group": x["specific_group"],
        }, new_slots))
        # db.slot.create_many(data=new_slots)
    return {"message": "successful"}


@router.get('/drop_slot')
def drop_slot():
    db.slot.delete_many()
    return {"message": "successful"}


@router.get('/quick_course_fix')
def quick_course_fix():
    slots = db.slot.find_many(include={"course": True})
    print(slots[0])
    for slot in slots:
        if not slot.course_name:
            db.slot.update(where={"id": slot.id}, data={
                "course_name": slot.course.description if slot.course else ""})
    return {"message": "successful"}


@router.get('/connect_slot_course_group')
def connect_slot_course_group():
    slots = db.slot.find_many(where={"specific_group": {
        "in": ["RFL-INTER", "RFL-BEGIN-M1", "RFL-BEGIN-M2", "RFL-BEGIN-BACH"]}})
    for slot in slots:
        course = db.course.find_first(
            where={"short_name": slot.specific_group})

        if course:
            db.slot.update(data={
                "course": {
                    "connect": {
                        "id": course.id
                    }
                }
            }, where={"id": slot.id})
    return {"message": "successful"}


@router.get('/course_abbrevation_validgroup')
def fill_course_abbrevation():
    courses = db.course.find_many(
        where={"is_elective": True},
        include={"time_slots": True})
    final_names = dict(MS_ELECTIVE_NAMES)
    final_names.update(BS4_ELECTIVE_NAMES)
    final_names.update(BS3_ELECTIVE_NAMES)
    for course in courses:
        if course.time_slots:
            valid_group = course.time_slots[0].specific_group
            db.course.update(data={
                "valid_group": valid_group,
                "short_name": final_names[course.description][0],
            }, where={"id": course.id})
    return {"message": "successful"}
