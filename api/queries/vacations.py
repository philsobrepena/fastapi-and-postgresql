from pydantic import BaseModel
from typing import List, Union, Optional
from datetime import date
from queries.pool import pool

class Error(BaseModel):
    message: str

#fastapi / basemodels are for ENDPOINTS not database

# class Thought(BaseModel):
#     private_thoughts: str
#     public_thoughts: str

class VacationIn(BaseModel):
    name: str
    from_date: date
    to_date: date
    thoughts: Optional[str]

class VacationOut(BaseModel):
    id: int
    name: str
    from_date: date
    to_date: date
    thoughts: Optional[str]

class VacationRepository:
    def update(self, vacation_id: int, vacation: VacationIn) -> Union[VacationOut, Error]:
        try:
            #connect database
            with pool.connection() as conn:
                #get a cursor
                with conn.cursor() as db:
                    db.execute(
                        """
                        UPDATE vacations
                        SET name = %s
                            , from_date = %s
                            , to_date = %s
                            , thoughts = %s
                        WHERE id = %s
                        """,
                        [
                            vacation.name,
                            vacation.from_date,
                            vacation.to_date,
                            vacation.thoughts,
                            vacation_id
                        ]
                    )
                    old_data = vacation.dict()
                    return VacationOut(id=vacation_id, **old_data)
        except Exception as e:
            print(e)
            return {"message": "could not update vacation"}
###GET
    def get_all(self) -> Union[Error, List[VacationOut]]:
        try:
            #connect database
            with pool.connection() as conn:
                #get a cursor
                with conn.cursor() as db:
                    #run SELECT statement
                    result = db.execute(
                    """
                    SELECT id, name, from_date, to_date, thoughts
                    FROM vacations
                    ORDER BY from_date;
                    """
                    )

                    ## map and filter
                    result = []
                    # for record in db:
                    #     vacation = VacationOut(
                    #         id=record[0],
                    #         name=record[1],
                    #         from_date=record[2],
                    #         to_date=record[3],
                    #         thoughts=record[4],
                    #     )
                    #     result.append(vacation)
                    # return result

                    ## List comprehension version of above
                    return [
                        VacationOut(
                            id=record[0],
                            name=record[1],
                            from_date=record[2],
                            to_date=record[3],
                            thoughts=record[4],
                        )
                        for record in db
                    ]

        except Exception as e:
            print(e)
            return {"message": "could not get vacations"}
###POST
    def create(self, vacation: VacationIn) -> VacationOut:
        #connect to database
        with pool.connection() as conn:
            # get a cursor (something to run SQL with)
            with conn.cursor() as db:
                # run INSERT statement
                result = db.execute(
                    """
                    INSERT INTO vacations
                        (name, from_date, to_date, thoughts)
                    VALUES
                        (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    [
                    vacation.name,
                    vacation.from_date,
                    vacation.to_date,
                    vacation.thoughts
                    ]
                )
                id = result.fetchone()[0]
                # return new data
                # old_data = vacation.dict()
                # # return{"message": "error"}
                # return VacationOut(id=id, **old_data)
                return self.vacation_in_to_out(id, vacation)

    def vacation_in_to_out(self, id:int, vacation: VacationIn):
        old_data = vacation.dict()
        return VacationOut(id=id, **old_data)

    def delete(self, vacation_id: int) -> bool:
        try:
            #connect to database
            with pool.connection() as conn:
                # get a cursor (something to run SQL with)
                with conn.cursor() as db:
                    # run INSERT statement
                    result = db.execute(
                        """
                        DELETE FROM vacations
                        WHERE id = %s
                        """,
                        [vacation_id]
                    )
        except Exception as e:
            print(e)
            return {"message": "could not delete vacation"}


###this doesnt work yet
    def get_one(self, vacation_id: int) -> Optional[VacationOut]:
        try:
            #connect to database
            with pool.connection() as conn:
                # get a cursor (something to run SQL with)
                with conn.cursor() as db:
                    # run INSERT statement
                    result = db.execute(
                        """
                        SELECT id
                            , name
                            , from_date
                            , to_date
                            , thoughts
                        FROM vacations
                        WHERE id = %s
                        """,
                        [vacation_id]
                    )
                    record = result.fetchone()
                    if record is None:
                        return None
                    return self.record_to_vacation_out(record)
        except Exception as e:
            print(e)
            return {"message": "could not get that vacation"}
